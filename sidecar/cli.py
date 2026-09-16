import argparse
import json
import sys
from pathlib import Path

from sidecar.classifier import get_classifier

def main():
    parser = argparse.ArgumentParser(
        description="PhotoOrganizer Sidecar CLI - Teste manual do classificador SigLIP"
    )
    parser.add_argument("image_path", type=str, help="Caminho para a imagem a ser classificada.")
    parser.add_argument("--raw", action="store_true", help="Exibe os scores brutos de todas as categorias.")

    args = parser.parse_args()
    image_path = Path(args.image_path)

    if not image_path.exists():
        print(f"Erro: O arquivo '{image_path}' não foi encontrado.")
        sys.exit(1)

    print("Carregando o modelo SigLIP (isso pode levar alguns segundos na primeira vez)...")
    try:
        classifier = get_classifier()
    except Exception as e:
        print(f"Erro ao inicializar o classificador: {e}")
        sys.exit(1)

    print(f"Classificando '{image_path.name}'...")
    try:
        scores = classifier.classify_image(image_path)
        results = classifier.evaluate_tags(scores)

        print("\n" + "="*50)
        print("RESULTADOS DA CLASSIFICAÇÃO")
        print("="*50)
        
        if results["is_utility"]:
            p_util = results["primary_utility"]
            print(f"[UTILITARIO] Detectado: {p_util['key']} (Score: {p_util['score']:.4f})")
            print(f"[DESTINO] Sugestão de Pasta : {p_util['destination']}")
        else:
            print("[COMUM] Foto Comum (Nenhum utilitário detectado)")

        print("\nTags Gerais Detectadas:")
        if results["general_tags"]:
            for tag in results["general_tags"]:
                print(f" - {tag['key']:<20} | Score: {tag['score']:.4f} | Destino: {tag['destination']}")
        else:
            print(" - Nenhuma tag geral detectada (todas abaixo do limite de 0.35)")

        if args.raw:
            print("\nScores Brutos (Todas as Categorias):")
            print(json.dumps(scores, indent=2))

    except Exception as e:
        print(f"\nErro durante a classificação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
