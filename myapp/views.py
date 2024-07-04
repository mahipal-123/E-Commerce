
from django.shortcuts import render,redirect
from.models import *
import random
import requests
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import razorpay
from django.views.decorators.cache import never_cache
# Create your views here.

@never_cache
def index(request):
    user = User.objects.get(email=request.session['email'])
    try:
        if user.usertype=="buyer":
            product = Product.objects.all()
            return render(request,"index.html",{'product':product})
        else:
            return render(request,"sindex.html")
    except Exception as e:
        msg = e
        return render(request,"index.html",{'msg':msg})


def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')
@never_cache
def signup(request):
    if request.method=="POST":
        try:
            msg = "Email is already exist"
            user = User.objects.get(email=request.POST['email'])
            return render(request,'login.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                usertype = request.POST['usertype'],    
                name = request.POST['name'],
                email = request.POST['email'],
                mobile = request.POST['mobile'],
                password = request.POST['password'],
                profile = request.FILES['profile']       
                )
                msg = "Signup Sucessfully!!"
                return render(request,'login.html',{'msg':msg})
            
            else:
                msg = "Password & confirm password does not match!!"
                return render(request,'signup.html',{'msg':msg})
                
       

    else:
         return render(request,'signup.html')
@never_cache
def login(request):
    if request.method=="POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                request.session['email']=user.email
                request.session['profile']=user.profile.url

                if user.usertype=="buyer":
                    return redirect('index')
                else:
                    return redirect('sindex')

            else:
                msg = "Password does not match!!"
                return render(request,'login.html',{'msg':msg})
            
        except:
            msg = "Email is not registered"
            return render(request,'login.html',{'msg':msg})

    else:
        return render(request,'login.html')
@never_cache    
def logout(request):
    
    del request.session['email']
    del request.session['profile']
    return  redirect('login')


def cpass(request):
    user = User.objects.get(email=request.session['email'])
    if request.method=="POST":
        
        if user.password==request.POST['opass']:
            if request.POST['npassword']==request.POST['cnpassword']:
                user.password=request.POST['npassword']
                user.save()
                msg = "Password Updated Sucessfully!!"
                if user.usertype=="buyer":
                    return render(request,'index.html',{'msg':msg})
                else:
                    return render(request,'sindex.html',{'msg':msg})

            else:
                msg = "New Password & confirm new password does not match!!"
                if user.usertype=="buyer":
                    return render(request,'cpass.html',{'msg':msg})

                else:
                    return render(request,'scpass.html',{'msg':msg})
                     
        else:
            msg = "Old Password does not match!!"
            if user.usertype=="buyer":
                return render(request,'cpass.html',{'msg':msg})
            else:
                return render(request,'scpass.html',{'msg':msg})
            
        

    else:
        if user.usertype=="buyer":
            return render(request,'cpass.html')
        else:
            return render(request,'scpass.html')
        


def fpass(request):
    if request.method=="POST":
        try:
            user = User.objects.get(mobile=request.POST['mobile'])
            mobile = request.POST['mobile']
            otp = random.randint(1001,9999)
            

            url = "https://www.fast2sms.com/dev/bulkV2"

            querystring = {"authorization":"EM5TxhCfzI9UyJ80Nijw7soGmOrVaAbtQ3nFZeRYqdB2KgWv61ikQ0M538obtfGCvKAlR7xrVXF6mOY9","variables_values":str(otp),"route":"otp","numbers":mobile}

            headers = {
                'cache-control': "no-cache"
            }

            response = requests.request("GET", url, headers=headers, params=querystring)
            request.session['mobile']=user.mobile
            request.session['otp']=otp
            return render(request,'otp.html')
        except:
            msg = "Mobile Number does not exists!!"
            return render(request,'fpass.html',{'msg':msg})
            
    else:
        return render(request,'fpass.html')

def otp(request):
    otp = int(request.session['otp'])
    uotp = int(request.POST['uotp'])
    try:
        if otp==uotp:
            del request.session['otp']
            return render(request,'newpass.html')    
            
        else:
            msg = "Invalid Otp"
            return render(request,'otp.html',{'msg':msg})
            
    except:
        pass


def newpass(request):
    if request.method=="POST":
        user = User.objects.get(mobile = request.session['mobile'])

        if request.POST['npassword']==request.POST['cnpassword']:
            user.password=request.POST['npassword']
            user.save()
            msg = "Password Updated Sucesfully!!"
            return render(request,'login.html',{'msg':msg})
        
        else:
            msg = "New password & confirm new password does not match!!"
            return render(request,'newpass.html',{'msg':msg})

    else:
        return render(request,'newpass.html')

    
def uprofile(request):
    user = User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.name = request.POST['name']
        user.mobile=request.POST['mobile']
        try:
            user.profile=request.FILES['profile']
            user.save()
        except:
            pass
        
        request.session['profile']=user.profile.url
        user.save()
        if user.usertype=="buyer":
            return render(request,'index.html',{'user':user})
        else:
             return render(request,'sindex.html',{'user':user})

    else:
        if user.usertype=="buyer":
            return render(request,'uprofile.html',{'user':user})
        else:
            return render(request,'sprofile.html',{'user':user})
        
def sindex(request):
    try:
        user = User.objects.get(email=request.session['email'])
        if user.usertype=="buyer":
            return render(request,"index.html")
        else:
            return render(request,"sindex.html")

    except:
        return redirect("login") 
    

   

def sadd(request):
    user = User.objects.get(email= request.session['email'])
    
    if request.method=="POST":
        try:
            Product.objects.create(
            user = user,
            pcategory = request.POST['pcategory'],
            pprice = request.POST['pprice'],
            pdesc = request.POST['pdesc'],
            pname = request.POST['pname'],
            pimage = request.FILES['pimage']     
            )
            msg = "Product Added Sucesfully!!"
            return render(request,'sindex.html',{'msg':msg})
        
        except Exception as e:
            print(e)
            msg = "You missing something!!"
            return render(request,'sadd.html',{'msg':msg})
    else:
        return render(request,'sadd.html')
        
def sview(request):
    user = User.objects.get(email = request.session['email'])
    product = Product.objects.filter(user=user) 
    return render(request,'sview.html',{'product':product})

def pdetails(request,pk):
    user = User.objects.get(email = request.session['email'])
    product = Product.objects.get(pk=pk) 

    return render(request,'pdetails.html',{'product':product})


def edit(request,pk):
    user = User.objects.get(email = request.session['email'])
    product = Product.objects.get(pk=pk)
    if request.method=="POST":
        product.pcategory = request.POST['pcategory']
        product.pname = request.POST['pname']
        product.pprice = request.POST['pprice']
        product.pdesc = request.POST['pdesc']
        try:
            product.pimage = request.FILES['pimage']
        except:
            pass
        product.save()
        msg = "Product Updated Sucessfully!!"
        return render(request,'sindex.html',{'msg':msg})
        
    else:
        return render(request,'edit.html',{'product':product})

def delete(request,pk):
    user = User.objects.get(email = request.session['email'])
    product = Product.objects.get(pk=pk)
    product.delete()
    return redirect('sindex')

def shop(request):
    try:
        user = User.objects.get(email = request.session['email'])
        print(user)
        product = Product.objects.all()
        w = False
    
        wish = Wishlist.objects.get(product=product)
        w = True
        return render(request,'shop.html',{'product':product,'w':w})
    except:
        product = Product.objects.all()
        return render(request,'shop.html',{'product':product})

    

def bppdetails(request,pk):
    user = User.objects.get(email = request.session['email'])
    product = Product.objects.get(pk=pk) 

    return render(request,'bppdetails.html',{'product':product})


def addwish(request,pk):
     try:
        user = User.objects.get(email = request.session['email'])
        product = Product.objects.get(pk=pk)
        w = False
        
        Wishlist.objects.create(user=user,product=product)
        
        
        return redirect ('wishlist')
     except:
         return redirect("login")


def wishlist(request):
    user = User.objects.get(email = request.session['email'])
    w = False
    try:
        wish = Wishlist.objects.filter(user=user)
        w = True
    except:
        pass
    return render (request,'wishlist.html',{'wish':wish,'w':w})


def dwish(request,pk):
    user = User.objects.get(email = request.session['email'])
    wish = Wishlist.objects.filter(user=user,pk=pk)
    wish.delete()
    return redirect ('wishlist')

    


def addcart(request,pk):
     try:
        user = User.objects.get(email = request.session['email'])
        product = Product.objects.get(pk=pk)
        Cart.objects.create(user=user,product=product,tprice=product.pprice,
                            cqty =1,
                            cprice=product.pprice,
                            payment = False)
        return redirect ('cart')
     except:
         return redirect("login")
def cart(request):
    user = User.objects.get(email = request.session['email'])
    cart = Cart.objects.filter(user=user,payment=False)
    net = 0
   
    for i in cart:
        net+=i.tprice

    if net>=20000:
        ship = 0

    else:
        ship=100

    sc = net+ship
    client = razorpay.Client(auth = (settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': sc * 100, 'currency': 'INR', 'payment_capture': 1})
    
    context = {
                    'payment': payment,
                    #'book':book,  # Ensure the amount is in paise
                }


   
    return render (request,'cart.html',{'cart':cart,'net':net,'ship':ship,'sc':sc,'context':context})


def dcart(request,pk):
    user = User.objects.get(email = request.session['email'])
    cart = Cart.objects.filter(user=user,pk=pk)
    cart.delete()
    return redirect ('cart')


def changeqty(request,pk):
    c = Cart.objects.get(pk=pk)
    print(c)
    c.cqty = int(request.POST['cqty'])
    c.save()
    c.tprice = c.cprice*c.cqty
    print(c.tprice)
    c.save()
    return redirect("cart")

def sucess(request):
    try:
        print(request.session['email'])
        user = User.objects.get(email=request.session['email'])
        cart=Cart.objects.filter(user=user)
        for i in cart:
            i.payment=True
            i.save()
        return render(request,'sucess.html',{'cart':cart})
    
    except Exception as e:
        print(e)
        return render(request,'index.html')
    
def myorder(request):
    user = User.objects.get(email=request.session['email'])
    cart=Cart.objects.filter(user=user,payment=True)
    return render(request,'myorder.html',{'cart':cart})
    

