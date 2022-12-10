//Get all the UI objects for manipulation
let searchButton = document.getElementById("search");
let inputSearch = document.getElementById("search-box-input");
let resultsContainer = document.getElementById("searchResultsContainer");
let ranker = document.getElementById("documentTypeDropdown");
let resultsList = document.getElementById("search-results");
let lastItem = '';
//Add Click event listener for the search button
searchButton.addEventListener("click", async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  //Utilizing chrome extension scripting library execute script to send the page text and search string
  //to backend api for searchinging
  //The executeScript executes the searchText function in the current active tabs context and scrapes the text of the HTML document
  //On success calls the fetch data to retrieve the ranked results.
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: searchText,
  },
  (response) => { 
    fetchData(response[0].result, inputSearch.value, ranker.value).then((data) => {
        searchButton.innerText = 'Search';
        resultsList.innerHTML = '';
        //Construct results list
        for(const item of data.search_results) {
          const li = document.createElement("li");
          li.innerText = item;
          li.addEventListener("click", async() => {
            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              func: elemsContainingText,
              args: [item]
            });
          })
          resultsList.appendChild(li);
        }
        let x = JSON.stringify(data.search_results);
        console.log(x);
        
    });
  });
  
});

//Function to fetchData from the backend
//Currently the server runs on the local machine
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
// current page to extract the current tabs to text to search
function searchText() {
  return document.body.innerText;
}

function elemsContainingText(item) {
  console.log('item',item);
  let elementList = [...document.querySelectorAll("p,h1,h2,h3,h4,h5,h6,li,span")];
  console.log(elementList);
  for (let el of elementList) {
    if (el.innerText.includes(item)) {
      console.log(el);
      el.style.backgroundColor="yellow";
    }
  }
  return;
}