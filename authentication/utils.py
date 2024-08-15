from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from .models import CustomUser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import requests


load_dotenv()


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access')
        if not access_token:
            return None
        
        try:
            # Decode the access token
            decoded_token = AccessToken(access_token)
            user_id = decoded_token.get('user_id')
            username = decoded_token.get('username')
            
            # Retrieve user details from the database
            user = CustomUser.objects.filter(id=user_id, username=username).first()
            if user is None:
                raise AuthenticationFailed(_('User not found.'))
        
        except (AccessToken.InvalidToken, CustomUser.DoesNotExist):
            raise AuthenticationFailed(_('Invalid token or user does not exist.'))
        
        return (user, None)
   
def search_youtube(query: str, language: str) -> dict:
    params = {
        'part': 'snippet',
        'q': query,
        'key': os.environ['Youtube_API'],
        'type': 'video',
        'videoCaption': 'any',
        'relevanceLanguage': language,
        'safeSearch': 'none',
        'maxResults': 50
    }
    response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
    response.raise_for_status()
    return response.json()


def SafeSearchModel(query: str) -> str:
    api_key = os.environ['Gemini_API']
    llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", api_key=api_key)

    prompt_template = PromptTemplate(
        input_variables=["query"],
        template=
        ("You are an AI assistant that helps determine the appropriateness of search queries. "
         "The text provided should only relate to specific categories such as:\n"
         "- Motivational content\n"
         "- Educational videos or tutorials\n"
         "- Technology-related content\n"
         "- Stories or poems\n"
         "- Spiritual content\n"
         "- Cartoons\n\n"
         "If the text is related to these categories, respond with 'yes.' If it is unrelated or includes "
         "inappropriate content, respond with 'no.'\n\n"
         "Here is the text to evaluate:\n\"{query}\""))
    formatted_prompt = prompt_template.format(query=query)

    message = HumanMessage(content=formatted_prompt)

    response = llm.invoke([message])
    response_text = response.content.strip()

    if response_text.lower() == 'yes':
        return 'Allowed'
    else:
        return 'Not Allowed'