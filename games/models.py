from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):

    GAME_TYPES = [
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('FPS', 'FPS'),
        ('Racing', 'Racing'),
        ('RPG', 'RPG'),
        ('MOBA', 'MOBA'),
        ('Sports', 'Sports'),
        ('Simulation', 'Simulation'),
        ('Strategy', 'Strategy'),
    ]

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount_percent = models.IntegerField(default=0)

    game_type = models.CharField(
        max_length=50,
        choices=GAME_TYPES,
        default='Action'
    )
    image_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to='games/',
        blank=True,
        null=True
    )

    def final_price(self):

        if self.discount_percent > 0:

            discount = (
                self.original_price *
                self.discount_percent
            ) / 100

            return self.original_price - discount

        return self.original_price

    def __str__(self):
        return self.title


class Purchase(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    purchased_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"


class Wishlist(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"


class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} cart {self.game.title}"