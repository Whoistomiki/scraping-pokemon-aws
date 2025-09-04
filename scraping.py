import requests
import os
import time
import boto3

s3_client = boto3.client('s3')
bucket_name = 'test-poke-img'  

def setup_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_image(url, file_path, session):
    try:
        response = session.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"Erreur lors du téléchargement de {url}: {str(e)}")
        return False

def upload_to_s3(file_path, bucket_name, s3_key):
    try:
        s3_client.upload_file(
            file_path, 
            bucket_name, 
            s3_key,
            ExtraArgs={'ContentType': 'image/png'}
        )
        print(f"✅ Upload réussi : {s3_key}")
        return True
    except Exception as e:
        print(f"❌ Erreur upload S3 : Failed to upload {file_path} to {bucket_name}/{s3_key}: {e}")
        return False

def get_last_processed_index():
    """Récupère l'index du dernier Pokémon traité"""
    try:
        with open('progress.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_progress(index):
    """Sauvegarde l'index du dernier Pokémon traité"""
    with open('progress.txt', 'w') as f:
        f.write(str(index))

def main():
    # Base URL de l'API PokeAPI
    base_url = "https://pokeapi.co/api/v2"
    output_dir = "pokemon_images"
    create_directory_if_not_exists(output_dir)
    
    session = setup_session()
    pokemon_count = 0
    
    # Récupérer le dernier index traité et définir la taille du lot
    start_index = get_last_processed_index()
    batch_size = 20
    
    try:
        print("Récupération de la liste des Pokémon...")
        response = session.get(f"{base_url}/pokemon?limit=1000")
        response.raise_for_status()
        pokemons = response.json()['results']
        total_pokemon = len(pokemons)
        end_index = min(start_index + batch_size, total_pokemon)
        current_batch = pokemons[start_index:end_index]
        
        print(f"Traitement des Pokémon {start_index + 1} à {end_index} sur {total_pokemon}")
        print("Début du téléchargement des images...")
        
        batch_count = 0
        for pokemon in current_batch:
            try:
                pokemon_url = pokemon['url']
                response = session.get(pokemon_url)
                response.raise_for_status()
                pokemon_data = response.json()
                img_url = pokemon_data['sprites']['other']['official-artwork']['front_default']
                
                if img_url:
                    pokemon_id = str(pokemon_data['id']).zfill(3)
                    pokemon_name = pokemon_data['name'].lower()
                    file_name = f"{pokemon_id}_{pokemon_name}.png"
                    file_path = os.path.join(output_dir, file_name)
                    
                    if not os.path.exists(file_path):
                        if download_image(img_url, file_path, session):
                            batch_count += 1
                            pokemon_count += 1
                            print(f"Image téléchargée ({batch_count}/{len(current_batch)}): {file_name}")
                            
                            # Upload sur S3
                            s3_key = f"images/pokemon/{file_name}"
                            if upload_to_s3(file_path, bucket_name, s3_key):
                                os.remove(file_path)
                            
                            time.sleep(0.5)
                    else:
                        print(f"L'image existe déjà: {file_name}")
                        
            except Exception as img_error:
                print(f"Erreur lors du traitement du Pokémon {pokemon['name']}: {str(img_error)}")
                continue
        
        # Sauvegarder la progression
        save_progress(end_index)
        
        remaining = total_pokemon - end_index
        print(f"\nLot terminé ! {batch_count} images ont été téléchargées dans ce lot.")
        print(f"Il reste {remaining} Pokémon à traiter.")
        if remaining > 0:
            print("Relancez le script pour traiter le prochain lot.")
                
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
        if pokemon_count > 0:
            print(f"{pokemon_count} images ont été téléchargées avant l'erreur")

if __name__ == "__main__":
    main()
