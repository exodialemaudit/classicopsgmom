import logging
from openai import OpenAI
from football_debate.ai_config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Envoie un prompt au modèle OpenAI et renvoie la réponse générée.
    
    Args:
        prompt (str): Le prompt à envoyer au modèle
        model (str): Le modèle à utiliser (par défaut: gpt-3.5-turbo)
        
    Returns:
        str: La réponse générée par le modèle
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error("Erreur OpenAI : %s", e)
        return "Désolé, une erreur s'est produite lors de la génération de la réponse." 