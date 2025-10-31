from django.shortcuts import render, redirect
from .forms import CustomerCreationForm

# Home View
def home(request):
    return render(request, 'home.html')

# Register View
def register(request):
    if request.method == 'POST':
        # User is submitting the form
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save() # This creates and saves the new user
            # Redirect to the login page after successful registration
            return redirect('login') 
    else:
        # User is just visiting the page
        form = CustomerCreationForm()
    
    # Render the template with the form
    return render(request, 'register.html', {'form': form})