import os
import tensorflow as tf
import numpy as np
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Signature ,SignatureComparison 
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, r'C:\Users\user\Desktop\Signature_comparison\signature_project\signature_verification_model (1).h5')
vgg_model = tf.keras.models.load_model(model_path, compile=False, safe_mode=True)
feature_extractor = tf.keras.Model(inputs=vgg_model.inputs, outputs=vgg_model.layers[-3].output)


def preprocess_image(img_path):
    """Load and preprocess an image for feature extraction"""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.vgg16.preprocess_input(img_array)
    return img_array


def verify_signatures(anchor_path, test_path, threshold=0.85):
    """Compare two signatures and return similarity score"""
    anchor_features = feature_extractor.predict(preprocess_image(anchor_path))
    test_features = feature_extractor.predict(preprocess_image(test_path))

    similarity = cosine_similarity(anchor_features, test_features)[0][0]
    return similarity, similarity >= threshold



import uuid

def save_signature(image_file, prefix):
    """ Save uploaded signature with a unique filename """
    unique_name = f"{prefix}_{uuid.uuid4().hex[:8]}_{image_file.name}"
    signature = Signature(image=image_file)
    signature.image.name = unique_name  # Set unique filename
    signature.save()
    return signature.image.path




def home(request):
    if request.method == 'POST':
        reference_image = request.FILES.get('reference_image')
        original_image = request.FILES.get('original_image')
        forged_image = request.FILES.get('forged_image')

        if not reference_image or not original_image or not forged_image:
            messages.error(request, "Please upload all three images.")
            return redirect('home')

        # DEBUG: Print received files
        print("📂 Received Reference Image:", reference_image)
        print("📂 Received Original Image:", original_image)
        print("📂 Received Forged Image:", forged_image)

        # Save images in correct order
        ref_signature = Signature(image=reference_image)
        orig_signature = Signature(image=original_image)
        forg_signature = Signature(image=forged_image)

        ref_signature.save()
        orig_signature.save()
        forg_signature.save()


        ref_path = ref_signature.image.path
        orig_path = orig_signature.image.path
        forg_path = forg_signature.image.path


        orig_similarity, is_original_genuine = verify_signatures(ref_path, orig_path)
        forg_similarity, is_forged_genuine = verify_signatures(ref_path, forg_path)

        # Convert values for session storage
        request.session['orig_similarity'] = float(round(orig_similarity * 100, 2))
        request.session['is_original_genuine'] = int(is_original_genuine)
        request.session['forg_similarity'] = float(round(forg_similarity * 100, 2))
        request.session['is_forged_genuine'] = int(is_forged_genuine)



        SignatureComparison.objects.create(
            reference_image=reference_image,
            original_image=original_image,
            forged_image=forged_image,
            orig_similarity=round(orig_similarity * 100, 2),
            forg_similarity=round(forg_similarity * 100, 2),
        )

        # Store correct images in session
        request.session['reference_image_url'] = ref_signature.image.url
        request.session['original_image_url'] = orig_signature.image.url
        request.session['forged_image_url'] = forg_signature.image.url

        print("✅ Saved Reference Image:", ref_signature.image.url)
        print("✅ Saved Original Image:", orig_signature.image.url)
        print("✅ Saved Forged Image:", forg_signature.image.url)

        return redirect('result')

    return render(request, 'home.html')



# def result(request):
#     """Display signature verification results"""
#     orig_similarity = request.session.get('orig_similarity', 0)
#     is_original_genuine = bool(request.session.get('is_original_genuine', 0))

#     forg_similarity = request.session.get('forg_similarity', 0)
#     is_forged_genuine = bool(request.session.get('is_forged_genuine', 0))


#     print(f"Original Similarity from session: {orig_similarity}")
#     print(f"Forged Similarity from session: {forg_similarity}")

#     return render(request, 'result.html', {
#         'orig_similarity': orig_similarity,
#         'is_original_genuine': is_original_genuine,
#         'forg_similarity': forg_similarity,
#         'is_forged_genuine': is_forged_genuine
#     })

from django.conf import settings

def result(request):
    reference_image_url = request.session.get('reference_image_url', "")
    original_image_url = request.session.get('original_image_url', "")
    forged_image_url = request.session.get('forged_image_url', "")

    print("🖼 Reference Image:", reference_image_url)
    print("🖼 Original Image:", original_image_url)
    print("🖼 Forged Image:", forged_image_url)


    orig_similarity = request.session.get('orig_similarity', 0)
    forg_similarity = request.session.get('forg_similarity', 0)

    is_original_genuine = bool(request.session.get('is_original_genuine', 0))
    is_forged_genuine = bool(request.session.get('is_forged_genuine', 0))

    context = {
        "reference_image_url": reference_image_url,
        "original_image_url": original_image_url,
        "forged_image_url": forged_image_url,
        "orig_similarity": orig_similarity,
        "is_original_genuine": is_original_genuine,
        "forg_similarity": forg_similarity,
        "is_forged_genuine": is_forged_genuine
    }

    return render(request, "result.html", context)

def history(request):
    comparisons = SignatureComparison.objects.all().order_by('-created_at')[:10]  # Get the latest 10 comparisons
    return render(request, 'history.html', {'comparisons': comparisons})