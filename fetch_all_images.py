import json
import subprocess
import sys
import yaml
import csv


KEYS = ('image', 'queueSidecarImage')


def get_images(document):
    images = []

    if isinstance(document, list):
        for item in document:
            if isinstance(item, (list, dict)):
                images += get_images(item)
    elif isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, (dict, list)):
                images += get_images(value)
            else:
                for search in KEYS:
                    if search == key:
                        images.append(value)
    else:
        raise Exception(f'What to do with {document}?')

    return images

def main():
    print('kustomize build...')
    kustomize = subprocess.run(
        ['kustomize', 'build'],
        capture_output=True,
    )
    if kustomize.returncode != 0:
        print(kustomize.stdout)
        print(kustomize.stderr)
        print(f'kustomize build command exit code: {kustomize.returncode}')
        print('Aborting')
        sys.exit(kustomize.returncode)

    print('Loading YAML documents...')
    documents = [
        yaml.safe_load(document)
        for document in kustomize.stdout.split(b'\n---')
    ]

    print('Getting images...')
    old_images = []
    with open('./images.csv', 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)

        print("Writing images to file...")
        for document in documents:
            for image in get_images(document):
                old_images.append(image)
                writer.writerow([image])
    
    print("Finished getting images...")



if __name__ == '__main__':
    main()