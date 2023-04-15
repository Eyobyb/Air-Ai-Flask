from langchain.llms import OpenAI
import asyncio
from dotenv import load_dotenv
from .utils import conversation_context_builder, json_loader, is_air_quality_in, is_follow_up, white_space_remover
from .context_utils import get_context, add_context
from .actions import position_finder, location_checker, summeriy_generator, default_llm, follow_up_question_checker, follow_up_question_generator, api_data_fetcher, summery_data_cleaner

load_dotenv()
llm = OpenAI(temperature=0)

# can you compare the air qualities in bangladish , usa,japan or ethiopia
# which country has the biggest air quality problem bangladish , usa,japan and ethiopia


async def is_follow_up_answer(user_input: str, context: str) -> bool:
    #    is_follow_up
    task = asyncio.create_task(follow_up_question_checker(user_input, context))
    task_value = await task
    check_value = is_follow_up(task_value)
    return check_value


async def result_generator(user_input, context):
    result = {
        "content": "",
        "role": 'assistant',
        "air_quality_data": []
    }
    if is_air_quality_in(user_input):
      
        location_task = asyncio.create_task(
            location_checker(user_input))
        location_task_data = await location_task

        filter_data = json_loader(location_task_data)
        if filter_data.get('fq') != "":
            result["content"] = filter_data.get('fq')
        else:
            locations = ', '.join(filter_data.get('locations'))
            coordinate_data_task = asyncio.create_task(
                position_finder(locations))
            coordinates = await coordinate_data_task
            coordinates = json_loader(coordinates)
            api_data_feature_task = asyncio.create_task(
                api_data_fetcher(coordinates))
            api_data_feature_data = await api_data_feature_task
            data_for_summery = summery_data_cleaner(api_data_feature_data)
            summery_task = asyncio.create_task(
                summeriy_generator(user_input, data_for_summery))
            summery_task_data = await summery_task
            result['content'] = summery_task_data
            result['air_quality_data'] = api_data_feature_data['location_and_pollutant'] if 'location_and_pollutant' in api_data_feature_data else api_data_feature_data

    else:
        llm_task = asyncio.create_task(default_llm(user_input, context))
        llm_data = await llm_task
        llm_data = white_space_remover(llm_data)
        result['content'] = llm_data
    return result


async def action_planner(user_input, session_id):
    context_task = asyncio.create_task(get_context(session_id))
    context = await context_task
    context = conversation_context_builder(context)
    final_data = {}
    follow_up_question_checker_task = asyncio.create_task(
        is_follow_up_answer(user_input, context))
    follow_up_question_checker_value = await follow_up_question_checker_task
    if (follow_up_question_checker_value):
        follow_up_generator_task = asyncio.create_task(
            follow_up_question_generator(user_input, "context"))
        follow_up_question_value = await follow_up_generator_task
        final_data_taks = asyncio.create_task(
            result_generator(follow_up_question_value, context))
        final_data = await final_data_taks
    else:

    
        final_data_taks = asyncio.create_task(
            result_generator(user_input, context))
        final_data = await final_data_taks
    add_context({"content": user_input, "role": "user",
                "air_quality_data": []}, session_id)
    add_context(final_data, session_id)
    final_data['session_id'] = session_id
    return final_data


async def main(user_input, session_id):

    task = action_planner(user_input, session_id)
    task = await task
    return task
