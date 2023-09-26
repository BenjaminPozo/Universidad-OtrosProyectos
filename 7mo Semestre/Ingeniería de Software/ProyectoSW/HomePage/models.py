from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Representa una transaccion de un usuario
class Transaction(models.Model):
    OPCIONES_TRANSACCION=(
        ('I','INGRESO'),
        ('E','EGRESO')
        )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default= timezone.now)
    transaction_type = models.CharField(max_length=1,choices=OPCIONES_TRANSACCION)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    comment = models.TextField()
    
    def __str__(self):
        return self.transaction_type