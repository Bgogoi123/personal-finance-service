# This file collects all models for a general visibility. Anyone can just import "Base" from here, and all models will automatically be loaded into memory.

from src.utils.db import Base
from src.auth.models import UsersModel
from src.categories.models import CategoriesModel
from src.payment_options.models import PaymentOptionsModel
from src.roles.models import RolesModel
from src.transaction.models import TransactionsModel