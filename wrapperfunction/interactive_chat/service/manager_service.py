import json

from fastapi import HTTPException

from wrapperfunction.interactive_chat.integration.openai_connector import assistant_chat_completion, chat_completion
from wrapperfunction.interactive_chat.model.interactive_chat_model import ActionResponse, GetForm, Status, ToolCall
from wrapperfunction.interactive_chat.service import functions

manager_function_descriptions = [
    {
        "type": "function",
        "function": {
            "name": "approve_vacation",
            "description": "Approves the vacation request for the employee with the given employee name and departemnt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose vacation request is to be approved."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department of the employee whose vacation request is to be approved."
                    }
                },
                "required": ["employee_name","employee_department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "disapprove_vacation",
            "description": "Disapproves the vacation request for the employee with the given employee name and departemnt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose vacation request is to be disapproved."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department of the employee whose vacation request is to be approved."
                    }
                },
                "required": ["employee_name","employee_department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pending_vacation",
            "description": "Pending the vacation request for the employee with the given employee name and departemnt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The name of the employee whose vacation request is to be disapproved."
                    },
                    "employee_department": {
                        "type": "string",
                        "description": "The department of the employee whose vacation request is to be approved."
                    }
                },
                "required": ["employee_name","employee_department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_vacation_forms_by",
            "description": "Returns all vacation requests for employees in the specified fillter.ex:to return all vaction for a Department of Status ",
            "parameters": {
                "type": "object",
                "properties": {
                  "coulomn_name": {
                        "type": "string",
                        "description": "The name of the cuolomn for which vacation requests should be retrieved. values should be on of the following(Type,Employee Name,ID,Manager Name,Department,Start-date,End-date,Total days,Status)"
                    },
                    "value": {
                        "type": "string",
                        "description": "The name of the value for which cuolomn in vacation requests should be retrieved."
                    }
                },
                "required": ["coulomn_name","value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_vacation_forms",
            "description": "Returns all vacation requests for employees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The manager prompt to show all the forms."
                    }
                },
                "required": ["text"]
            }
        }
    }
]

manager_chat_history = [
    {"role":"system","content":"your name is(Mo3een/مُعين)you are a Manager AI Assistant that helps him to do daily tasks, be helpful ,Friendly, kind and handsome and cute and use emojies, and talk with the manager with his langueg in en go en if ar go ar,whn you asked to search for department search useing these choeses(AI,PM,HR,SE,IT) "}
    ]
 

async def manager_chat(prompt: str):
    print("\n\n1\n\n")
    # # Add a user question to the thread and update chat history
    
    try:
        print("\n\n2\n\n")
        print(f"Chat_History: {manager_chat_history}")
        
        print("\n\n3\n\n")
        assistant_response = assistant_chat_completion(prompt, manager_chat_history, manager_function_descriptions)
        
        print("\n\n4\n\n")
        print(f"Assist_RES:{assistant_response}")
        
        print("\n\n5\n\n")
        response_message = assistant_response.choices[0].message
        
        print(f"Response MSG:{response_message}")
        
        manager_chat_history.append(response_message)
        
        
        if response_message.tool_calls:
            
            functions = [ToolCall(function_name=tool_call.function.name, function_args=json.loads(tool_call.function.arguments)) for tool_call in response_message.tool_calls]

            print(f"Tool_Calls:{response_message.tool_calls}")
            
            for tool_call in response_message.tool_calls:
                manager_chat_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": tool_call.function.arguments
                    })
            return ActionResponse(actions=functions, message="None")
        
        return ActionResponse(actions=None, message=response_message.content) 

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
async def manager_approve_action(arguments:Status):
    try:
        result = functions.approve_vacation(arguments.employee_name, arguments.employee_department)
        final_message = manager_generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def manager_disapprove_action(arguments:Status):
    try:
        
        result = functions.disapprove_vacation(arguments.employee_name, arguments.employee_department)
        final_message = manager_generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def manager_pending_action(arguments:Status):
    try:
        result = functions.pending_vacation(arguments.employee_name, arguments.employee_department)
        final_message = manager_generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": result,
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def manager_getForm_action(arguments: GetForm):
    try:
        print(f'Argument-Type:{type(arguments)}')
        print(f'Argument:{arguments}')
        
        result = functions.get_forms(arguments.coulomn_name,arguments.value)
        final_message = await manager_generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": str(result),
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def manager_getAllForms_action():
    try:
        result = functions.get_all_forms()
        final_message = await manager_generate_final_resopnse(result)
        return {
            "isComplete":True,
            "response": str(result),
            "message": final_message
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))     

async def manager_generate_final_resopnse(results):
    msg =''' f"Here are the results of your requests: {results}. print the result in a good and easy to read way "
             f"Based on these results,ask to approve,disapprove or revert to pending, "
              f"notify your team, or filter or take other action? Please allways suggest a next step. depends on the request result"
            f"important nate: speek arabic if the manager is speeking arabic in the previose messages, do not translate the name keep it as is, show all the results dont hide any thing, the manager should see the all detials"'''
            
            
            # Get the final response based on the results of all tool calls
    try:
        final_response = chat_completion(msg,manager_chat_history)
                
        manager_chat_history.append({
                    "role": "assistant",
                    "content": final_response.choices[0].message.content
                })
        print(f"Final Result: {final_response}")
                
        return final_response.choices[0].message.content
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
