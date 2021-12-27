// Html elements
const choices_El = Array.from(document.querySelectorAll('.choice-text'));
const correctAnswer = ['1', '2', '3', '4'];
const btnNext = document.querySelector('#btn-next');

// control var
let score = 0;
let questionCounter = 0;
let availableQuestions = [];
var questionsIndex;

// Load the question
var questionJson = JSON.parse($.getJSON({'url': "/static/js/tests/depression/questions.json", 'async': false}).responseText);
const MAX_QUESTIONS = questionJson.questions.length;
const answer_Lists = questionJson.choices;

// sum total
var totals = 0;

// array current answer
var currentAnswer = [0, 0, 0, 0, 0];
var questionIndexArr = [];

// store the question
var questionArr = [...questionJson.questions];

// Start the test
startTest = () => {
    questionCounter = 0;
    score = 0;
    availableQuestions = [...questionJson.questions];
    getNewQuestion();
}

// Score increment
incrementScore = (num) => {
    score += num;
}

// sum all answer
sumAllAnswer = () => {
    for (var i = 0; i < 5; i++) {

        // sum the answer
        incrementScore(parseInt(currentAnswer[i]));
    }

    // empty the current answer array
    currentAnswer = [0, 0, 0, 0, 0];

    // empty the question index array
    questionIndexArr = [];
}

// Get the new question
getNewQuestion = () => {
    
    // If questions is done, stop the test, send result
    if(availableQuestions.length === 0 ) {
        // remove the prevent leave script
        window.onbeforeunload = null;

        var form = $('<form action="/tests/health/depression/result" method="post">' +
            '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrftoken + '">' +
            '<input type="hidden" name="score" value="' + score + '">' +
            '</form>');
        $('body').append(form);
        form.submit();

        return;
    }

    var question_El;
    var x = 0;

    while (x < 5) {
        question_El = document.querySelector(`#question-${x+1}`);
        // Counter
        questionCounter++;
        
        // Get the questions
        questionsIndex = Math.floor(Math.random() * availableQuestions.length);

        currentQuestion = availableQuestions[questionsIndex].q;

        // index
        questionIndexArr.push(availableQuestions[questionsIndex].id);

        // Set the question
        question_El.innerText = currentQuestion;
        // remove the question from the list of available questions
        availableQuestions.splice(questionsIndex, 1);

        x++;
    }
    
}

choices_El.forEach(choice => {
    choice.addEventListener('click', e => {
        
        // Get answers
        const selectedChoice = e.target;
        var selectedAnswer = selectedChoice.dataset['number'];
        const id = selectedChoice.dataset['id'];

        // If user play around with inspect element, things will break that's why we tell them to not do it
        if (selectedAnswer == undefined || correctAnswer.includes(selectedAnswer) == false) {
            selectedAnswer = 0;
            alert('Tolong jangan main-main dengan jawabannya!');
        }

        // check for all items with the same id
        let allChoices = document.querySelectorAll(`[data-id="${id}"]`);
        allChoices.forEach(choice => {
            // check if class contains selected
            if (choice.className.includes('selected')) {
                // if it does, remove it and change the color back to normal
                choice.classList.remove('selected');
                choice.style.backgroundColor = '#fbfcfe';
            }
            currentAnswer[id - 1] = 0;
        });

        // get the class of the element to change the color
        let className = selectedChoice.className;
        // change color of the selected choice
        if (className.includes('green')) {
            selectedChoice.classList.add('selected');
            selectedChoice.style.backgroundColor = '#9AE782';
            currentAnswer[id - 1] = selectedAnswer;
        } else {
            selectedChoice.classList.add('selected');
            selectedChoice.style.backgroundColor = '#61AEF2';
            currentAnswer[id - 1] = selectedAnswer;
        }
    })
})

// Next button
btnNext.addEventListener('click', e => {
    // check if all choices are selected
    if (currentAnswer.includes(0)) {
        alert('Silakan pilih semua jawaban!');
    } else {
        // if yes, sum the answer
        sumAllAnswer();
        // get new question
        getNewQuestion();
        // reset the color
        choices_El.forEach(choice => {
            choice.classList.remove('selected');
            choice.style.backgroundColor = '#fbfcfe';
        });
        // move to the top of the page
        window.scrollTo(0, 0);

    }
})

// MAIN
startTest()