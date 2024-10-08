from django.db import models

class ExchangeRate(models.Model):
    time = models.CharField(max_length=50, db_column='time', primary_key=True)  
    yen_100 = models.CharField(max_length=50, db_column='100엔')  
    dollar = models.CharField(max_length=50, db_column='달러') 
    yuan = models.CharField(max_length=50, db_column='위안')  

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'exchange_rate' 

    def __str__(self):
        return f"{self.time} - {self.dollar} USD, {self.yen_100} JPY, {self.yuan} CNY"

class Kospi(models.Model):
    time = models.CharField(max_length=50, db_column='time', primary_key=True)  
    kospi = models.CharField(max_length=50, db_column='kospi지수')  
    kosdaq = models.CharField(max_length=50, db_column='kosdaq지수')
    volume = models.CharField(max_length=50, db_column='거래량_코스닥시장')
    amount = models.CharField(max_length=50, db_column='거래대금_코스닥시장')

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'kospi' 

    def __str__(self):
        return f"{self.time} - {self.kospi} KOSPI, {self.kosdaq} KOSDAQ, {self.volume} 거래량, {self.amount} 거래대금"

class newssentiment(models.Model):
    time = models.CharField(max_length=50, db_column='time', primary_key=True)  
    sentiment = models.CharField(max_length=50, db_column='newssentiment')  

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'newssentiment' 

    def __str__(self):
        return f"{self.time} - {self.sentiment}"

class InterestRates(models.Model):
    time = models.CharField(max_length=50, db_column='time', primary_key=True)
    koribor_12m = models.CharField(max_length=50, db_column='koribor(12개월)')
    treasury_10y = models.CharField(max_length=50, db_column='국고채(10년)')
    treasury_2y = models.CharField(max_length=50, db_column='국고채(2년)')
    treasury_5y = models.CharField(max_length=50, db_column='국고채(5년)')
    call_rate_bank_securities = models.CharField(max_length=50, db_column='콜금리(1일, 은행증권금융차입)')
    call_rate_total = models.CharField(max_length=50, db_column='콜금리(1일, 전체거래)')
    call_rate_broker_deal = models.CharField(max_length=50, db_column='콜금리(1일, 중개회사거래)')
    corporate_bond_aa = models.CharField(max_length=50, db_column='회사채(3년, aa-)')
    corporate_bond_bbb = models.CharField(max_length=50, db_column='회사채(3년, bbb-)')

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'market_interest_rates'  

    def __str__(self):
        return f"{self.time} - Koribor 12M: {self.koribor_12m}, Treasury 10Y: {self.treasury_10y}, Treasury 2Y: {self.treasury_2y}, Treasury 5Y: {self.treasury_5y}, Call Rate Bank Securities: {self.call_rate_bank_securities}, Call Rate Total: {self.call_rate_total}, Call Rate Broker Deal: {self.call_rate_broker_deal}, Corporate Bond 3Y AA: {self.corporate_bond_3y_aa}, Corporate Bond 3Y BBB: {self.corporate_bond_3y_bbb}"
    
class HighKR(models.Model):
    name = models.CharField(max_length=100, db_column='name')  
    date = models.DateField(db_column='date', primary_key=True)  
    change = models.DecimalField(max_digits=10, decimal_places=2, db_column='change')  

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'high_volatility_kr'  

    def __str__(self):
        return f"{self.name} on {self.date} - Change: {self.change}"

class HighUS(models.Model):
    name = models.CharField(max_length=100, db_column='name')  
    date = models.DateField(db_column='date', primary_key=True)  
    change = models.DecimalField(max_digits=10, decimal_places=2, db_column='change')  

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정
        db_table = 'high_volatility_us'  

    def __str__(self):
        return f"{self.name} on {self.date} - Change: {self.change}"


class StockKRTop100(models.Model):
    date = models.DateField(db_column='date')
    name = models.CharField(db_column='name', primary_key=True, max_length=100)
    code = models.CharField(db_column='code')

    class Meta:
        managed = False
        db_table = 'kr_top100'

    def __str__(self):
        return f"{self.date} - {self.name} ({self.code})"
    
class StockUSTop100(models.Model):
    name = models.CharField(db_column='name', primary_key=True, max_length=100)
    code = models.CharField(db_column='code')
    excode = models.CharField(db_column='excode')

    class Meta:
        managed = False
        db_table = 'ustop100'

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.excode}"

class StockKRHistory(models.Model):
    date = models.DateField(db_column='date', primary_key=True)  # `date`와 `name`을 복합 키로 사용하기 위해 primary_key=True 제거
    name = models.CharField(max_length=100, db_column='name')  
    code = models.CharField(max_length=20, db_column='code') 
    open_value = models.DecimalField(max_digits=8, decimal_places=2, db_column='open_value') 

    class Meta:
        managed = False
        db_table = 'kr_stock_data'
        unique_together = (('date', 'name'),)  # 복합 키를 설정

    def __str__(self):
        return f"{self.date} - {self.name} ({self.code}) - {self.open_value} KRW"

class StockUSHistory(models.Model):
    date = models.DateField(db_column='date', primary_key=True)  # `date`와 `name`을 복합 키로 사용하기 위해 primary_key=True 제거
    name = models.CharField(max_length=100, db_column='name')  
    code = models.CharField(max_length=20, db_column='code') 
    open_value = models.DecimalField(max_digits=8, decimal_places=2, db_column='open_value') 

    class Meta:
        managed = False
        db_table = 'us_stock_data'
        unique_together = (('date', 'name'),)  # 복합 키를 설정

    def __str__(self):
        return f"{self.date} - {self.name} ({self.code}) - {self.open_value} USD"
