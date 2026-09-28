import json

from marketing_agent.services.prompt_service import PromptService


def get_learning_prompt() -> dict:
    prompt_service = PromptService()
    
    return prompt_service.load_prompt(
        team="learning",
        prompt_name="system", 
    )
    
    
def main() -> None:
    prompt = get_learning_prompt()
    print(
        json.dumps(
            prompt,
            ensure_ascii=False,
            indent=2,
        )
    )
    
if __name__ == "__main__":
    main()
