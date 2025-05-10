import textwrap
import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import re

GOOGLE_API_KEY = 'AIzaSyC11_rV1NlFqnVZx9AQBzOqJYFSd3bGZ4k'
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def generate_gemini_response(prompt):
    response = model.generate_content(prompt)
    return response.text
@csrf_exempt
def chat_bot_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        response = generate_gemini_response(user_message)
        return JsonResponse({'response': response})
    return render(request, 'chatbot/chatbot.html') 


# Predefined responses
responses = {
    "how to book": "To book, visit our website or app, choose a service, select a date and time, and confirm payment.",
    "cancel booking": "To cancel a booking, go to 'My Bookings', select the booking, and click 'Cancel'. Cancellation fees may apply.",
    "payment options": "We accept credit/debit cards, UPI, and net banking. EMI options are also available.",
    "refund policy": "Refunds are processed within 5-7 business days based on the payment method used.",
    "contact support": "You can contact our support team at support@example.com or call +1-800-123-4567."
}

def get_response(user_message):
    user_message = user_message.lower()
    for pattern, response in responses.items():
        if re.search(pattern, user_message):
            return response
    return "I'm sorry, I didn't understand. Please ask about bookings, cancellations, or payments."

@csrf_exempt
def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            response = get_response(user_message)
            return JsonResponse({"response": response})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)
