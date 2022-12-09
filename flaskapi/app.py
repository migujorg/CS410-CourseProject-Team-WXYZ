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

'''
API for search queries
Expects the HTML text{corpus}, search string {search} and ranking method {ranker}
 Returns list of top-5 results according to the selected ranker
 Text Cleaning:
   1. Split lines
   2. Get rid of lines with one word or less
   3. create data set each sentence in a line
   4. Write to dataset file from the configuration file
   5. Run the text search algorithm
   6. Return search results
   This is setup for single-user mode using filesystem to store the corpus
'''
@app.route('/search', methods=['POST'])
def parameters():
    
    #purge old index
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

    results = []
    if len(original_doc) > 0:
        results = search(search_string, original_doc, ranker)

    if len(results) == 0 :
        results = ["No Results!"]

    response = jsonify(search_results=results)

    return response


'''
Helper functions to remove dirs
'''
def clean_dirs(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))

'''
Core ranking function
Uses metapy library to create inverted index via config.toml file
1. Preprocessing
    a. icu-tokenizer
    b. lowercase
    c. porter2-filter
    d. ngram-word 1

2. Create inverted index 
3. Instantiate BM25 ranker
3. create the query document
4. Run the ranker for the query and idx
5. Return top-5 hits
'''
def search(search_string, original_doc, ranker, cfg = 'config.toml'):
    print('Searching...')
    idx = metapy.index.make_inverted_index(cfg)
    print('Done idx...')
    ranker = metapy.index.OkapiBM25(k1=2.4,b=0.75,k3=400)
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

'''
Helper Function to retrieve configuration file for metapy
'''
def get_config(cfg = 'config.toml'):
    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    return cfg_d



if __name__ == '__main__':
    app.run(threaded=False)
