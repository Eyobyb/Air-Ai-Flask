import re
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import asyncio
from dotenv import load_dotenv

from .utils import get_polutant
load_dotenv()


llm = OpenAI(temperature=0)


async def follow_up_question_checker(user_input, conversation_context):
    follow_up_Prompt = PromptTemplate(
        input_variables=['user_input', 'context'],
        template="""
      you are an air quality assistant. I am going to provide you with a conversation we had . and just like an API return JSON value. 
  
     from the conversation, check the "user text" that was given. whether it is a location correction or clarification follow up answer.
    
     Conversation = {context}
     user text =  {user_input}
     
    desired output :
     {{ 
        "is_a_follow_up_answer": "True" or "False" , 
        "reason": why it is or it is not and be specific
     }}

     the desired output is json object only no other string 

     
    """
    )

    follow_up_checker = LLMChain(llm=llm, prompt=follow_up_Prompt)
    return follow_up_checker.run(context=conversation_context, user_input=user_input)


async def follow_up_question_generator(user_input, context):
    prompt = PromptTemplate(
        input_variables=['user_input', 'context'],
        template="""
    by going through the context and by combining user_input create a corrected 
    question.
     Example: 
          context = "
                    user: hi there.
                    assistant: hello how can I help you.
                    user: what is the air quality in my current position?
                    assistant: sorry I dont know what your current location is can you give me your city or country name?
                    user : sure my city name is ASSSSSE
                    assistant: sorry I don't know any location by the name ASSSSSE. can you correct it and send me back with the correct name?
                    "
          user_input = I meant to say assela
          answer:  what is the air quality in assela.

    Context: {context}
    user_input: {user_input}

    Answer: 
    
    """
    )
    follow_up_generator = LLMChain(llm=llm, prompt=prompt)
    return follow_up_generator.run(context=context, user_input=user_input)


async def location_checker(user_input):
    prompt = PromptTemplate(
        input_variables=['user_input'],
        template="""
        we are going to play a game. the game is about listing locations from a given text called context.
        the game rules are.
        . json output only
        . if one of the location that you found is unkown or only known to the Context writer. then write a question in fq for clarification about the given location.
        . you only ask a question about the unkown location not anything else

                    {{
                        "locations: list all locations mensioned in the QQ ,
                        "fq": 
                    }}
        
        context: {user_input}
        """
    )
    location_chain = LLMChain(llm=llm, prompt=prompt)
    return location_chain.run(user_input=user_input)


async def api_data_fetcher(lists):
    final_result = {"location_and_pollutant": []}

    for list in lists['coordinates']:
        lat = list['lat']
        lon = list['lon']
        location = list['location']
        if lat != 404 or lon != 404:
            response_task = asyncio.create_task(get_polutant(lat, lon))
            response = await response_task
            final_result['location_and_pollutant'].append(
                {"location": location, "data": response.get('data'), "error": response.get('error')})

    return final_result


async def position_finder(user_input):
    prompt = PromptTemplate(
        input_variables=['user_input'],
        template="""
    by going through the user listed locations return a json of lat and lon for each location 
    if location is not known set lat and lon 404
    
    desired ouput: 
{{ "coordinates":
    [
     $${{
     "location":"name of the location",
     "lat": lattitude of the location , 
     "lon": longtiude of the location 
     }}
    ]
    }}
    

    user_input: {user_input}

    Answer: 
    
    """
    )
    position_chain = LLMChain(llm=llm, prompt=prompt)
    return position_chain.run(user_input=user_input)


async def default_llm(user_input, context):
    prompt = PromptTemplate(
        input_variables=['user_input', 'context'],
        template=""" 
        you are a friendly air quality data assistant. 
        in the context you are the assistant and I am the user.
        if you are asked
        about what BAQIS it is a custom air quality index that creates a
        common indexing value where different nations have their own indexing 
        range.

        use the context as a pervious conversation 
        
        desired output: plain text
    
    
        user_question: {user_input}
        context: {context}
        Answer:
    """)
    default_chain = LLMChain(llm=llm, prompt=prompt)
    return default_chain.run(user_input=user_input, context=context)


async def summeriy_generator(user_input, data):
    prompt = PromptTemplate(
        input_variables=['user_input', 'context'],
        template="""
    from now on you are an air quality analist. so when are asked a 
    question by the user_input check your data from the context and answer only and only based on the context.

    baqi is a custom Air Quality Index where:
    value from 0-19 is poor 
    value from 20-39 is low 
    value from 40-59 Moderate
    value from 60-79 Good
    value from 80-100 Excellent

    if there is an error in the context return state it at the end

        

    user_input: {user_input}

    context: {context}

    Answer: 
    
    """
    )
    summery_chain = LLMChain(llm=llm, prompt=prompt)
    return summery_chain.run(user_input=user_input, context=data)


def summery_data_cleaner(data):
    pollutant_list = ""
    for item in data['location_and_pollutant']:
        final_string = 'location ' + item['location']
        if item['data'] != None:
            final_string = final_string + " baqi =" + \
                str(item['data']['indexes']['baqi']['aqi']) + '  pollutants'
            pollutants = item['data']['pollutants']

            for pollutant in pollutants:

                name = pollutants[pollutant]['display_name']
                ammount = pollutants[pollutant]['concentration']['value']
                unit = pollutants[pollutant]['concentration']['units']
                final_string = final_string + ' ' + \
                    name + ' ' + str(ammount) + unit + ', '
        else:
            final_string = final_string + \
                " error The location specified in the request is unsupported"
        pollutant_list = pollutant_list + final_string + '\n'

    return pollutant_list


# can you compare the air qualities in bangladish , usa,japan and ethiopia
# which country has the biggest air quality problem bangladish , usa,japan and ethiopia
