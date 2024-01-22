let departure_from_list = false;
let destination_from_list = false;
let popularCities = [];
let debounceTimer;
let filterTimer;

async function loadCitiesFromWiki() {
    return fetchData('/get_wiki_cities');
}

async function loadCities() {
    return fetchData('/get_cities');
}

async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data.data;
}

function filterCities(items, input_value) {
    const inputLower = input_value.toLowerCase();

    if (inputLower.length < 2) {
        return [];
    }

    const regex = new RegExp(`^${inputLower}`);

    const [exactMatchCities, otherCities] = items.reduce(([exactMatch, others], item) => {
        const itemLower = item.toLowerCase();

        if (regex.test(itemLower)) {
            isPopularCity(item) ? exactMatch.unshift(item) : others.push(item);
        }

        return [exactMatch, others];
    }, [[], []]);

    return [...exactMatchCities, ...otherCities];
}

function isPopularCity(city) {
    return popularCities.some(popularCity => city.toLowerCase().includes(popularCity.toLowerCase()));
}


async function handleInput(inputElement, list, items, input_value, otherList) {
    clearTimeout(debounceTimer);
    clearTimeout(filterTimer);

    debounceTimer = setTimeout(() => {
        filterTimer = setTimeout(async () => {
            const filtered_items = filterCities(items, input_value);
            const filtered_cities = filtered_items.filter(item => item.toLowerCase().startsWith(input_value.toLowerCase()));
            const filtered_regions = filtered_items.filter(item => !item.toLowerCase().startsWith(input_value.toLowerCase()));
            dropdownList(list, filtered_cities, filtered_regions, input_value, inputElement, otherList);

            if (inputElement.value.trim() !== '') {
                inputElement === departureInput ? departure_from_list = false : destination_from_list = false;
            }
        }, 0);
    }, 0);
}

function displayAllItems(list, display_items, input_value, inputElement) {
    list.innerHTML = '';

    const inputLower = input_value.toLowerCase();

    display_items.forEach(item => {
        const li = document.createElement('li');
        const lowerItem = item.toLowerCase();
        const index = lowerItem.indexOf(inputLower);

        if (index !== -1) {
            const before = document.createTextNode(item.substring(0, index));
            const match = document.createElement('span');
            match.className = 'highlight';
            match.textContent = item.substring(index, index + inputLower.length);
            const after = document.createTextNode(item.substring(index + inputLower.length));

            li.appendChild(before);
            li.appendChild(match);
            li.appendChild(after);
        } else {
            li.textContent = item;
        }

        li.addEventListener('click', function () {
            inputElement.value = item;
            list.style.display = 'none';
            if (list === departureCityList) {
                departure_from_list = true;
            } else if (list === destinationCityList) {
                destination_from_list = true;
            }
        });

        list.appendChild(li);
    });
}

function dropdownList(list, filtered_cities, filtered_regions, input_value, inputElement, otherList) {
    let itemsToDisplay = [];
    if (input_value !== '') {
        if (filtered_cities.length > 0) {
            itemsToDisplay = filtered_cities.slice(0, 5);
        } else if (filtered_regions.length > 0) {
            itemsToDisplay = filtered_regions.slice(0, 5);
        }
    }
    list.style.display = itemsToDisplay.length > 0 ? 'block' : 'none';
    if (itemsToDisplay.length > 0) {
        displayAllItems(list, itemsToDisplay, input_value, inputElement);
    }
    if (otherList) {
        otherList.style.display = 'none';
    }
}

const departureInput = document.getElementById('departure_city');
const targetInput = document.getElementById('destination_city');
const departureCityList = document.getElementById('departure_city-list');
const destinationCityList = document.getElementById('destination_city-list');

async function init() {
    const [departureCities, destinationCities] = await Promise.all([loadCities(), loadCities()]);
    popularCities = await loadCitiesFromWiki();

    const handleInputChange = (inputElement, list, items, otherList) => {
        handleInput(inputElement, list, items, inputElement.value, otherList);
    };

    departureInput.addEventListener('input', () => handleInputChange(departureInput, departureCityList, departureCities, destinationCityList));
    targetInput.addEventListener('input', () => handleInputChange(targetInput, destinationCityList, destinationCities, departureCityList));

    document.addEventListener('click', event => {
        if (event.target !== departureInput && event.target !== targetInput) {
            departureCityList.style.display = 'none';
            destinationCityList.style.display = 'none';
        }
    });
}

window.onload = init;



//

// Блок валидации

//


const valid = ["box_length", "box_width", "box_height", "box_weight", "destination_city", "departure_city"];
const numerical = ["box_length", "box_width", "box_height", "box_weight"];
const label_status = document.getElementById('status'); 


function check_inputs() {
  remove_error_styles();
  if (validate_inputs_value()) {
    label_status.innerText = "Заполните все поля";
  } 
}


function remove_error_styles() {
  for (const id of valid) {
    const element = document.getElementById(id);
    element.classList.remove('error');
  }
}


function validate_inputs_value() {
  let any_inputs_empty = false;
  let non_numerical_input = false;

  for (const id of valid) {
    const element = document.getElementById(id);
    const value = element.value.trim();

    if (!value) {
      any_inputs_empty = true;
    }

    if (numerical.includes(id)) {
      if (value === '' || !/^[0-9]+([.,][0-9]+)?$/.test(value)) {
        non_numerical_input = true;
      }
    }
  }

  if (any_inputs_empty) {
    return true;
  } else if (!destination_from_list) {
    label_status.innerText = "Выберите город получателя из меню";
    targetInput.value = '';
    apply_error_styles_for_destination();
  }  else if (!departure_from_list) {
      label_status.innerText = "Выберите город отправителя из меню";
      departureInput.value = '';
      apply_error_styles_for_departure();
    
  } else if (non_numerical_input) {
    label_status.innerText = "Заполните корректные числовые значения";
    apply_error_styles_for_nymerical();
  } else {
    label_status.innerText = "Успешно";
    //Действия при успешном вводе
  }

  return false;
}

function apply_error_styles_for_nymerical() {
  for (const id of numerical) {
    const element = document.getElementById(id);
    const isValid = element.value.trim() !== '' && /^[0-9]+([.,][0-9]+)?$/.test(element.value.trim());
    if (!isValid) {
      element.classList.add('error');
    } else {
      element.classList.remove('error');
    }
  }
}

function apply_error_styles_for_departure() {
  const element = document.getElementById("departure_city");
    if (!departure_from_list) {
      element.classList.add('error');
    } else {
      element.classList.remove('error');
  }
}


function apply_error_styles_for_destination() {
  const element = document.getElementById("destination_city");
    if (!destination_from_list) {
      element.classList.add('error');
    } else {
      element.classList.remove('error');
  }
}