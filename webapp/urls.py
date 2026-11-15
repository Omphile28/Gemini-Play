from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path("5_cards/", views.five_cards, name="five_cards"),
    path("draw/", views.draw_from_deck, name="draw_from_deck"),
    path("take-discard/", views.take_discard, name="take_discard"),
    path("replace/<int:position>/",views.replace_card, name="replace_card"),
    path("reset/",views.reset_game,name="reset_game"),
    path("discard-selected/", views.discard_selected, name="discard_selected"),
    path("sekaku/", views.sekaku, name="sekaku"),
    path("sekaku/play/<int:pile>/", views.play_pile, name="play_pile"),
    path("sekaku/reset/", views.reset_sekaku, name="reset_sekaku"),
    path("topten/", views.topten, name="topten"),
    path("topten/draw/", views.draw_topten, name="draw_topten"),
    path("topten/make-ten/", views.make_ten, name="make_ten"),
    path("topten/reset/", views.reset_topten, name="reset_topten"),
    path("topten/select/<int:index>/",views.select_topten,name="select_topten"),
    path("dice/", views.dice, name="dice"),
    path("roll_dice/", views.roll_dice, name="roll_dice"),
    path("reset_dice/", views.reset_dice, name="reset_dice"),
    path("race100/", views.race100, name="race100"),
    path("race100/roll/", views.race100_roll, name="race100_roll"),
    path("race100/reset/", views.race100_reset, name="race100_reset"),
    path("slots/", views.slots, name="slots"),
    path("slots/spin/", views.spin_slots, name="spin_slots"),
]