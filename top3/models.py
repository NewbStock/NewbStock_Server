from django.db import models

class StockRank(models.Model):
    country = models.CharField(max_length=255, db_column='country')  
    ticker = models.CharField(max_length=255, db_column='ticker', primary_key=True)   
    name = models.CharField(max_length=255, db_column='name')     
    percent = models.FloatField(db_column='percent')               
    rank = models.IntegerField(db_column='rank')                

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'stock_rank' 

    def __str__(self):
        return f"{self.country} - {self.ticker} {self.name} {self.percent} {self.rank}"