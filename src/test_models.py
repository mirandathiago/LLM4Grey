import importlib
import os
from config import LLM_MODELS, PROMPT_DIR
from validate.outputvalidator import OutputValidator
import json



example_discussion = {       
        "id": 1264,
        "title": "What criteria should be considered when deciding to do work which goes beyond project scope?",
        "body": "Answering my recently asked question whether to \"deliver results when finished significantly prior to the agreed deadline\", Smandoli suggested to fill the slack with \"Look for places to exceed expectations, exceed the spec.\" I understand that deciding whether to do work which goes beyond defined project scope depends on a number of factors. Which ones do you consider to be particularly important to make a qualified decision?",
        "score": 5,
        "creationdate": "2011-03-26 16:34:23.687000",
        "viewcount": 160,
        "tags": "<politics><customer-satisfaction><relationships>",
        "answercount": 6,
        "favoritecount": 0,
        "userId": 699,
        "comments": [
            {
                "text": "@jmort253, yes I intentionally open a new question instead of commenting on Smandoli's answer on the previous question, because in my understanding the new question is about a wider scope and therefore deserves a separated question. Also, naturally I added part of my understanding of that topic as well, in order to give a hint into which direction my question is targeting. Do you think the question would be acceptable had I left the three bullet points?",
                "score": 1,
                "userId": 699
            }
        ]
    }


def build_user_prompt(template: str, discussion: dict) -> str:
    comments_text = "\n".join(f"- {c['text']}" for c in discussion["comments"])
    return (
        template.replace("<title>", discussion["title"])
                .replace("<body>", discussion["body"])
                .replace("<comments>", comments_text)
    )

def test_model(model_name: str, prompt_path: str, temperature: float = 0.0):
    print(f"\n🔍 Testing model: {model_name} | Temp: {temperature}\n")


    with open(os.path.join(prompt_path, "system.txt"), "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    with open(os.path.join(prompt_path, "user.txt"), "r", encoding="utf-8") as f:
        user_prompt = build_user_prompt(f.read().strip(), example_discussion)


    model_info = LLM_MODELS[model_name]
    module = importlib.import_module(f"models.{model_info['file']}")
    class_name = model_info['file'].replace("-", "_").capitalize()

    model_class = getattr(module, class_name)
    model_instance = model_class(api_key=model_info["api_key"])

    response_text = model_instance.execute(system_prompt, user_prompt, temperature)

    print("\n📤 Raw response:\n")
    print(response_text)


    try:
        print("\n✅ Validated OutputFormat:")
        response_json = OutputValidator.model_validate_json(response_text)
        print(response_json.model_dump())
    except Exception as e:
        print("\n⚠️ Could not validate response:")
        print(str(e))


if __name__ == "__main__":
    '''
    test_model(
        model_name="GPT-4o",
        prompt_path=os.path.join(PROMPT_DIR, "zero-shot-v1"),
        temperature=0.0
    )

    test_model(
        model_name="Gemini 2.0 Flash",
        prompt_path=os.path.join(PROMPT_DIR, "zero-shot-v1"),
        temperature=0.0
    )


    test_model(
        model_name="Claude 3.5 Sonnet",
        prompt_path=os.path.join(PROMPT_DIR, "zero-shot-v1"),  
        temperature=0.0
    )


    test_model(
        model_name="Grok 2",
        prompt_path=os.path.join(PROMPT_DIR, "zero-shot-v1"),  
        temperature=0.0
    )'''

    test_model(
        model_name="Deepseek R1",
        prompt_path=os.path.join(PROMPT_DIR, "zero-shot-v1"),  
        temperature=0.0
    )

