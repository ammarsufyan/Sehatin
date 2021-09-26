// Html elements
const question_El = document.querySelector('#question');
const choices_El = Array.from(document.querySelectorAll('.choice-text'));
const progressText_El = document.querySelector('#progressText');
const progressBarFull_El = document.querySelector('#progressBarFull');

// control var
let acceptingAnswers = true
let score_Kesepian = 0;
let score_Sosial = 0;
let questionCounter = 0;
let availableQuestions = [];
var questionsIndex;

// Load the question
var questionJson = JSON.parse($.getJSON({'url': "/static/js/tests/kesehatan-mental/questions.json", 'async': false}).responseText);
const MAX_QUESTIONS = questionJson.questions.length;
const answer_Lists = questionJson.choices;

// Start the test
startTest = () => {
    questionCounter = 0;
    score = 0;
    availableQuestions = [...questionJson.questions];
    getNewQuestion();
}

// Score increment
incrementScore = (num, type) => {
    switch (type) {
        case 'kesepian':
            score_Kesepian += num
            break;
        case 'sosial':
            score_Sosial += num
            break;
        default:
            break;
    }
}

// Get the new question
getNewQuestion = () => {
    // If questions is done, stop the test, send result
    if(availableQuestions.length === 0 || questionCounter > MAX_QUESTIONS) {
        var form = $('<form action="/tests/result" method="post">' +
            '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrftoken + '">' +
            '<input type="hidden" name="score_kesepian" value="' + score_Kesepian + '">' +
            '<input type="hidden" name="score_sosial" value="' + score_Sosial + '">' +
            '</form>');
        $('body').append(form);
        form.submit();
    }

    // Counter
    questionCounter++;
    progressText_El.innerText = `Question ${questionCounter} of ${MAX_QUESTIONS}`;
    progressBarFull_El.style.width = `${(questionCounter/MAX_QUESTIONS) * 100}%`;
    
    // Get the questions
    questionsIndex = Math.floor(Math.random() * availableQuestions.length);
    currentQuestion = availableQuestions[questionsIndex].q;

    // Set the question
    question_El.innerText = currentQuestion;

    // Fill the answers
    choices_El.forEach((choice, i)=> {
        choice.innerText =  answer_Lists[i];
    });

    acceptingAnswers = true;
}

choices_El.forEach(choice => {
    choice.addEventListener('click', e => {
        if(!acceptingAnswers) return

        acceptingAnswers = false;
        
        // Get answers
        const selectedChoice = e.target;
        /* const selectedAnswer = selectedChoice.dataset['number'] */ // old method

        // score dictionary, O(1)
        let scoreDict = {
            "Sangat sesuai": 4,
            "Sesuai": 3,
            "Tidak sesuai": 2,
            "Sangat tidak sesuai": 1
        }

        // get the score
        let score_Get = scoreDict[selectedChoice.innerText];

        // If user play around with inspect element, things will break that's why we tell them to not do it
        if (score_Get == undefined) {
            score_Get = 0;
            alert('Please do not play around with the answers!');
        }

        // increment the score
        incrementScore(score_Get, availableQuestions[questionsIndex].type);

        // Remove the questions from the array
        availableQuestions.splice(questionsIndex, 1);



        // Get new question
        getNewQuestion();
    })
})

// Start the game
startTest()