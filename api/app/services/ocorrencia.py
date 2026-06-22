import os
import json
import google.generativeai as genai # type: ignore

def executar_ocorrencia():
    try:
        api_key = os.getenv('API_KEY_GEMINI')
        if not api_key:
            raise ValueError("API_KEY_GEMINI not found in environment variables")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        dias_file = '/data/logs/rdo_geral/dias_avisados.json'
        if not os.path.exists(dias_file):
            raise FileNotFoundError(f"File not found: {dias_file}")
        
        with open(dias_file, 'r', encoding='utf-8') as f:
            dias = json.load(f)
        
        processed_count = 0
        for date, notified in dias.items():
            if notified:
                path = f'/data/media/RDO/{date}/Atividades/ocorrencias.txt'
                if os.path.exists(path):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if not content.strip():
                            print(f"Skipped {date}: empty file")
                            continue
                        
                        prompt = "Formate este texto de ocorrências de uma maneira clara e organizada, corrigindo erros gramaticais, melhorando a legibilidade e estruturando as informações de forma lógica."
                        
                        response = model.generate_content(prompt + "\n\n" + content)
                        revised_content = response.text
                        
                        revised_dir = f'/data/media/RDO/{date}/Atividades'
                        os.makedirs(revised_dir, exist_ok=True)
                        
                        revised_path = f'{revised_dir}/ocorrencia-revisado.txt'
                        with open(revised_path, 'w', encoding='utf-8') as f:
                            f.write(revised_content)
                        
                        print(f"Processed {date}")
                        processed_count += 1
                    except Exception as e:
                        print(f"Error processing {date}: {str(e)}")
                else:
                    print(f"File not found for {date}: {path}")
        
        return {"status": "completed", "processed": processed_count}
    
    except Exception as e:
        print(f"Error in executar_ocorrencia: {str(e)}")
        return {"status": "error", "error": str(e)}