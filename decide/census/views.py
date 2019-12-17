from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from census.models import Census
from django.contrib.auth.models import User
from voting.models import Voting



class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')


def listaVotantes(request, voting_id):
    census = list(Census.objects.filter(voting_id=voting_id))
    datos = []
    for c in census:
        user = list(User.objects.filter(pk=c.voter_id))[0]
        votacion = list(Voting.objects.filter(pk=c.voting_id))[0]
        tupla = (user, votacion)
        datos.append(tupla)
    return render(request, 'tabla.html', {'datos':datos, 'STATIC_URL':settings.STATIC_URL})
    

def listaCensos(request):
    census = list(Census.objects.all())
    datos = []
    for c in census:
        user = list(User.objects.filter(pk=c.voter_id))[0]
        votacion = list(Voting.objects.filter(pk=c.voting_id))[0]
        tupla = (user, votacion)
        datos.append(tupla)
    return render(request, 'tabla.html', {'datos':datos, 'STATIC_URL':settings.STATIC_URL})