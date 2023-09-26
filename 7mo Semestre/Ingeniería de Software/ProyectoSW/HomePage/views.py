from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from .forms import RegisterForm, LoginForm
from django.db.models import Sum



from .models import Transaction
from .forms import NewTransactionForm

from django.core.exceptions import ObjectDoesNotExist

# Representa la vista de la pagina de inicio
def home(request):
    if request.user.is_authenticated:
        #Entrega el saldo total del usuario obteniendo la suma de todos los ingresos y egresos
        context = {
            'title' : 'Home',
            #Se toma en cuenta la excepcion de que no existan transacciones de un tipo o ambos
            'saldo' : Transaction.objects.filter(author_id=request.user.id ,transaction_type='I').aggregate(Sum('amount'))['amount__sum'] - Transaction.objects.filter(author_id=request.user.id ,transaction_type='E').aggregate(Sum('amount'))['amount__sum'] if Transaction.objects.filter(author_id=request.user.id ,transaction_type='I').aggregate(Sum('amount'))['amount__sum'] is not None and Transaction.objects.filter(author_id=request.user.id ,transaction_type='E').aggregate(Sum('amount'))['amount__sum'] is not None else Transaction.objects.filter(author_id=request.user.id ,transaction_type='I').aggregate(Sum('amount'))['amount__sum'] if Transaction.objects.filter(author_id=request.user.id ,transaction_type='I').aggregate(Sum('amount'))['amount__sum'] is not None else -Transaction.objects.filter(author_id=request.user.id ,transaction_type='E').aggregate(Sum('amount'))['amount__sum'] if Transaction.objects.filter(author_id=request.user.id ,transaction_type='E').aggregate(Sum('amount'))['amount__sum'] is not None else 0,
            } # va por casos: Idealmente se espera fixear o hacer mas simple a futuro unu

        return render(request, 'HomePage/homePage.html', context)
    return render(request, 'HomePage/homePage.html')

# Se encarga de loguear al usuario
@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def login_view(request):
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            user = authenticate(request, username=loginform.cleaned_data['user'], password=loginform.cleaned_data['password'])
            if user is not None:
                login(request, user)
                next_page = request.POST.get('next', '/')
                return redirect(next_page)
            else:
                # mostrar mensaje de error
                pass
    else:
        loginform = LoginForm()
        next_page = request.GET.get('next', '/')
    return render(request, 'registration/login.html', {'loginform': loginform, 'next': next_page})

#Se encarga de registrar un nuevo usuario
@csrf_protect
@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def register_view(request):
    if request.method == 'POST':
        registerform = RegisterForm(request.POST)
        if registerform.is_valid():
            # Se inicializa el usuario con los datos ingresados
            user = User.objects.create_user(
                username=registerform.cleaned_data['user'],
                email=registerform.cleaned_data['email'],
                password=registerform.cleaned_data['password']
            )
            user.save()

            # Agregar al usuario al grupo de "Usuarios de transacciones"
            try:
                group = Group.objects.get(name='Usuarios de transacciones')
            except ObjectDoesNotExist: # Si el grupo no existe, se crea
                group = Group.objects.get_or_create(name='Usuarios de transacciones')
                group = Group.objects.get(name='Usuarios de transacciones')


            user.groups.add(group)

            return redirect('login')
    else:
        registerform = RegisterForm()
    return render(request, 'registration/registration.html', {'registerform': registerform})

#Se encarga de mostrar las transacciones del usuario
@login_required(login_url='/login/')
def transaction(request):
    context = {
        'transactions' : Transaction.objects.raw('SELECT * FROM HomePage_transaction WHERE author_id = %s', [request.user.id]),
        'title' : 'Transactions'
    }
    #Notamos que 'transactions' contiene todas las transacciones del usuario!
    return render(request, 'Transactions/transaction.html', context)

#Se encarga de añadir una transaccion mediante un formulario
@login_required(login_url='/login/')
def addTransaction(request):
    if request.method == 'POST':
        form = NewTransactionForm(request.POST)
        if form.is_valid():
            new_transaction = form.save(commit=False)   
            new_transaction.author_id = request.user.id
            new_transaction.save()
            return redirect('Transacciones del Usuario')  # Redirige a la página de transacciones después de guardar el formulario
    else:
        form = NewTransactionForm()
    
    return render(request, 'Transactions/add_transaction.html', {'form': form})

#Se obtiene la transaccion a modificar y se le pasa al formulario para que lo modifique o elimine
@login_required(login_url='/login/')
def modificarTransaction(request, transaction_id):
    #Se obtiene la transaccion a modificar
    transaction = Transaction.objects.get(id=transaction_id)
    #Se utiliza el formulario de añadir transaccion pero con los datos de la transaccion a modificar
    #Además se ven los casos modificar y eliminar

    if request.method == 'POST':
        form = NewTransactionForm(request.POST, instance=transaction) #Se le pasa la instancia de la transaccion a modificar
        
        #Se ve si se quiere modificar o eliminar
        if request.POST.get('modi'):  #Si se quiere modificar
            #print("modificar")
            if form.is_valid():
                new_transaction = form.save(commit=False)
                new_transaction.author_id = request.user.id
                new_transaction.save()
                return redirect('Transacciones del Usuario')
        if request.POST.get('del'): #Si se quiere eliminar
            #print("delete")
            transaction.delete()
            return redirect('Transacciones del Usuario')
    else:
        form = NewTransactionForm(instance=transaction)
            
    return render(request, 'Transactions/modificar_transaction.html', {'form': form})
       
