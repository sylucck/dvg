import graphene
from graphene_django import DjangoObjectType

#adding relay specification
from graphene import relay, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

from cookie.models import Category, Ingredient

# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)

#class CategoryType(DjangoObjectType):
class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        #fields = ("id", "name", "ingredients")
        filter_fields = ['name', 'ingredients']
        interfaces = (relay.Node, )

#class IngredientType(DjangoObjectType):
class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        #fields = ("id", "name", "notes", "category")
        interfaces = (relay.Node,)

class Query(graphene.ObjectType):
    #all_ingredients = graphene.List(IngredientType)
    #category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

    def resolve_all_ingredients(root, info):
        # We can easily optimize query count in the resolve method
        return Ingredient.objects.select_related("category").all()

    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
