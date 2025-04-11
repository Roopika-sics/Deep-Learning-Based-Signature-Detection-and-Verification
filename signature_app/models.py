from django.db import models

class Signature(models.Model):
    image = models.ImageField(upload_to='signatures/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    feedback = models.CharField(max_length=100,default=False)


class SignatureComparison(models.Model):
    reference_image = models.ImageField(upload_to="signatures/")
    original_image = models.ImageField(upload_to="signatures/")
    forged_image = models.ImageField(upload_to="signatures/")
    orig_similarity = models.FloatField()
    forg_similarity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"