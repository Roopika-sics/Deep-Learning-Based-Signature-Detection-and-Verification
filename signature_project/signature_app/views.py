from django.shortcuts import render, redirect
from .models import Signature
from PIL import Image
import imagehash

def home(request):
    if request.method == 'POST':
        if 'image1' in request.FILES and 'image2' in request.FILES:
            # Save the first signature
            signature1 = Signature(image=request.FILES['image1'])
            signature1.save()
            
            # Save the second signature
            signature2 = Signature(image=request.FILES['image2'])
            signature2.save()
            return redirect('result')
    
    return render(request, 'home.html')



def result(request):
    signatures = Signature.objects.all().order_by('-uploaded_at')[:2]
    if len(signatures) == 2:
        hash1 = imagehash.average_hash(Image.open(signatures[0].image))
        hash2 = imagehash.average_hash(Image.open(signatures[1].image))
        similarity = 100 - (hash1 - hash2) * 100 / len(hash1.hash) ** 2

        threshold = 80 
        match_result = "Match" if similarity >= threshold else "Not a Match"
        return render(request, 'result.html', {'match_result':match_result})

    
    return render(request, 'result.html', {'similarity': None})
