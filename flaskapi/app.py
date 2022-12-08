from flask import Flask, jsonify, request, json, after_this_request
import metapy
import pytoml
import os
import shutil

app = Flask(__name__)


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the Planetary API.'), 200


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response

@app.route('/search', methods=['POST'])
def parameters():
    
    #clean_dirs('./datas')
    clean_dirs('./idx')
    request_data = json.loads(request.data)
    corpus = request_data['corpus']
    search_string = request_data['search']
    ranker = request_data['ranker']

    stripped_page_text = "".join([s for s in corpus.strip().splitlines(True) if s.strip()])
    cfg_d = get_config('config.toml')

    dataset = cfg_d['dataset']
    filename = './' + dataset + '/' + dataset +'.dat'

    text_file = open(filename, "w")
    original_doc = []
    for line in stripped_page_text.splitlines():
        if len(line.split()) > 1:
            text_file.write(line + "\n")
            original_doc.append(line.rstrip())

    text_file.close()

    print('RECV search_string : {}'.format(search_string))
    print('RECV ranker : {}'.format(ranker))

    results = search(search_string, original_doc, ranker)

    if len(results) == 0 :
        results = ["No Results!"]

    response = jsonify(search_results=results)

    return response

def clean_dirs(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))

def search(search_string, original_doc, ranker, cfg = 'config.toml'):
    print('Searching...')
    idx = metapy.index.make_inverted_index(cfg)
    print('Done idx...')
    ranker = metapy.index.OkapiBM25(k1=2.4,b=0.75,k3=400) #metapy.index.JelinekMercer()
    print('Done Bm25...')
    query = metapy.index.Document()
    query.content(search_string.strip())
    print('Done query strip...')

    top_docs = ranker.score(idx, query, num_results=5)
    #top_docs = []
    print('Done ranking..')

    results = []
    for num, (d_id, _) in enumerate(top_docs):
        results.append(original_doc[d_id])

    print('Done looping..')
    print(results)
    clean_dirs('./idx')
    return results


def get_config(cfg = 'config.toml'):
    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    return cfg_d



if __name__ == '__main__':
    app.run(threaded=False)
