let searchButton = document.getElementById("search");
let inputSearch = document.getElementById("search-box-input");
let resultsContainer = document.getElementById("searchResultsContainer");
let ranker = document.getElementById("documentTypeDropdown");
let resultsList = document.getElementById("search-results");

searchButton.addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: searchText,
  },
  (response) => { 
    fetchData(response[0].result, inputSearch.value, ranker.value).then((data) => {
        searchButton.innerText = 'Search';
        resultsList.innerHTML = '';
        for(const item of data.search_results) {
            resultsList.innerHTML += "<li>" + item + "</li>";
        }
    });
  });
});

async function fetchData(corpus, search, ranker) {
    searchButton.innerHTML = '<i class="fa fa-refresh fa-spin"></i>Searching...';
    const url = "http://127.0.0.1:5000/search";
    data = {
        "corpus": corpus,
        "search" : search,
        "ranker": ranker
    };

    let results = await fetch(url, {
        method: 'POST',
        cache: 'no-cache',
        //mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json())  
      .then(json => {
        console.log(JSON.stringify(json));
        return json;
    })

    return results;
}

// The body of this function will be executed as a content script inside the
// current page
function searchText() {
  return document.body.innerText;
}