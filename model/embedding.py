import torch 
import torch.nn as nn 
import torch.nn.functional as F 
from torch.nn.utils import weight_norm 
import math 


class PositionalEmbedding(nn.Module):
    def __init__(self,d_model,max_len=512):
        super(PositionalEmbedding,self).__init__()

        pe = torch.zeros(max_len,d_model).float()
        pe.requires_grad = False
        position  = torch.arange(0,max_len).float().unsqueeze(1)
        div_term =(torch.arange(0,d_model,2).float() * - (math.log(10000.0)/d_model)).exp()


        pe[:,0::2] = torch.sin(position*div_term)
        pe[:,1::2] = torch.cos(position*div_term)

        pe = pe.unsqueeze(0)
        self.register_buffer('pe',pe)
    def forward(self,x):
        return self.pe[:,:x.size(1)]
    
class TokenEmbedding(nn.Module):
    def __init__(self,c_in,d_model):
        super(TokenEmbedding,self).__init__()
        padding = 1 if torch.__version__ >= '1.5.0' else 2 
        self.tokenConv = nn.Conv1d(in_channels = c_in,out_channels=d_model,kernel_size=3,
                                   padding=padding,padding_mode="circular",bias=False)
        for m in self.modules():
            if isinstance(m,nn.Conv1d):
                nn.init.kaiming_normal_(m.weight,mode="fan_in",nonlinearity='leaky_relu')
        
    def forward(self,x):
        x = self.tokenConv(x.permute(0,2,1)).transpose(1,2)
        return x 
    
class TemporalEmbedding(nn.Module):
    def __init__(self,d_model):
        super(TemporalEmbedding,self).__init__()

        minute_size = 4; hour_size = 24
        weekday_size = 7; day_size = 32; month_size = 13

        Embed = nn.Embedding
        self.fc = nn.Linear(5*d_model,d_model)
        self.minute_embed = Embed(minute_size,d_model)
        self.hour_embed = Embed(hour_size,d_model)
        self.weekday_embed =Embed(weekday_size,d_model)
        self.day_embed = Embed(day_size,d_model)
        self.month_embed = Embed(month_size,d_model)
    
    def forward(self,x):
        x = x.long()
        minute_x = self.minute_embed(x[:,:,4])
        hour_x = self.hour_embed(x[:,:,3])
        weekday_x = self.weekday_embed(x[:,:,2])
        day_x = self.day_embed(x[:,:,1])
        month_x  =self.month_embed(x[:,:,0])
        out =torch.cat((minute_x,hour_x,weekday_x,day_x,month_x),dim=2)
        out = self.fc(out)
        return out
    
class DataEmbedding(nn.Module):
    def __init__(self,c_in,d_model,dropout=0.1):
        super(DataEmbedding,self).__init__()

        self.value_embedding = TokenEmbedding(c_in=c_in,d_model=d_model)
        self.position_embedding = PositionalEmbedding(d_model=d_model)
        self.temporal_embedding = TemporalEmbedding(d_model=d_model)
        self.dropout = nn.Dropout(p=dropout)
    
    def forward(self,x,x_mark):
        x = self.value_embedding(x) + self.temporal_embedding(x_mark) + self.position_embedding(x)
        return self.dropout(x)

        
