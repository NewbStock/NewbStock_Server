from django.db import models

class USTOP100(models.Model):
    Name = models.CharField(max_length=100, db_column='name')
    Code = models.CharField(max_length=100, db_column='code')
    excode = models.CharField(max_length=100, db_column='excode')

    class Meta:
        db_table = 'ustop100'

    def __str__(self):
        return f"{self.Name} - {self.Code} {self.excode}"
    
class KRTOP100(models.Model):
    Date = models.DateField(db_column='date')
    Name = models.CharField(max_length=100, db_column='name')
    Code = models.CharField(max_length=100, db_column='code')

    class Meta:
        db_table = 'kr_top100'

    def __str__(self):
        return f"{self.Name} - {self.Code} {self.excode}"
    

class KRSTOCKDATA(models.Model):
    date = models.DateField(db_column='date')
    name = models.CharField(max_length=100 , db_column='name')
    code = models.CharField(max_length=50 , db_column='code')
    open_value = models.DecimalField(max_digits=8, decimal_places=2, db_column='open_value')

    class Meta:
        db_table = 'kr_stock_data'

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.date}"
    
class USSTOCKDATA(models.Model):
    date = models.DateField(db_column='date')
    name = models.CharField(max_length=100 , db_column='name')
    code = models.CharField(max_length=50 , db_column='code')
    open_value = models.DecimalField(max_digits=8, decimal_places=2, db_column='open_value')

    class Meta:
        db_table = 'us_stock_data'

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.date}"