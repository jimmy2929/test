from django.shortcuts import render , redirect

def callhtml(request,name):
    try:
        store_name = name
    except:
        errormessage = " (讀取錯誤!)"
    return render(request,"")