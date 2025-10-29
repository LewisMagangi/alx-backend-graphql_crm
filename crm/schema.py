import re
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order

# -------------------- Low Stock Mutation --------------------
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # No arguments needed

    updated_products = graphene.List(lambda: ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_list = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_list.append(product)
        return UpdateLowStockProducts(
            updated_products=updated_list,
            message=f"{len(updated_list)} products updated successfully."
        )

# -------------------- GraphQL Types --------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# -------------------- Mutations --------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Validate email uniqueness
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        # Validate phone format (if provided)
        if phone and not re.match(r"^\+?\d{1,3}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,9}$", phone):
            raise Exception("Invalid phone format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for record in input:
            try:
                name = record.get("name")
                email = record.get("email")
                phone = record.get("phone")

                if not name or not email:
                    raise Exception("Name and email are required")

                if Customer.objects.filter(email=email).exists():
                    raise Exception(f"Email '{email}' already exists")

                if phone and not re.match(r"^\+?\d{1,3}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,9}$", phone):
                    raise Exception(f"Invalid phone format for '{name}'")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created_customers.append(customer)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if Decimal(price) <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise Exception("No valid products found")
        if len(products) != len(product_ids):
            raise Exception("One or more product IDs are invalid")

        total_amount = sum(p.price for p in products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date or timezone.now()
        )
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)


# -------------------- Root Schema --------------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info, **kwargs):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
