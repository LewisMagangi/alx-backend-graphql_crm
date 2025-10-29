import graphene

# Import CRMQuery and CRMMutation using relative import when available, fallback to absolute import, and fallback placeholders.

from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
