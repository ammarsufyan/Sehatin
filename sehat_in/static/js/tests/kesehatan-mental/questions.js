const question = document.querySelector('#question');
const choices = Array.from(document.querySelectorAll('.choice-text'));
const progressText = document.querySelector('#progressText');
const scoreText = document.querySelector('#score');
const progressBarFull = document.querySelector('#progressBarFull');

let currentQuestion = {}
let acceptingAnswers = true
let score = 0
let questionCounter = 0
let availableQuestions = []

let questions = [
    {
        question: 'Seberapa sering kamu merasa cocok dengan orang-orang di sekitarmu?',
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 2,
    },
    {
        question:"Seberapa sering kamu merasa tidak memiliki sahabat?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 1,
    },
    {
        question: "Seberapa sering kamu merasa tidak bisa meminta bantuan ke siapapun?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 3,
    },
    {
        question: "Seberapa sering kamu merasa sendirian?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 1,
    }, 
    {
        question: "Seberapa sering kamu merasa menjadi bagian dari kelompok pertemanan?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa kamu memiliki banyak kesamaan dengan orang di sekitarmu?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa kamu tidak dekat dengan siapapun lagi?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa ide dan pendapatmu berbeda dengan orang-orang di sekitarmu?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',  
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa sebagai orang yang ramah dan mudah bergaul dengan orang lain?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa dekat dengan orang lain?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa dikucilkan oleh orang lain?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa hubungan kamu dengan orang lain tidak bermakna?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa tidak ada yang benar-benar memahamimu dengan baik?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa terasing dari orang lain?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa kamu bisa menemukan sahabat jika kamu memang menginginkannya?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa kamu memiliki orang yang benar-benar memahamimu?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa sebagai orang yang pemalu?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa orang-orang yang ada di sekitarmu tidak benar-benar bersamamu?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bahwa kamu memiliki teman untuk bercerita?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }, 
    {
        question: "Seberapa sering kamu merasa bisa meminta bantuan ke orang lain?",
        choice1: 'Tidak pernah',
        choice2: 'Jarang',
        choice3: 'Kadang-kadang',
        choice4: 'Selalu',
        answer: 3,
    }
]

const SCORE_POINTS = 100
const MAX_QUESTIONS = 20

startGame = () => {
    questionCounter = 0
    score = 0
    availableQuestions = [...questions]
    getNewQuestion()
}

getNewQuestion = () => {
    if(availableQuestions.length === 0 || questionCounter > MAX_QUESTIONS) {
        var form = $('<form action="/tests/result" method="post">' +
          '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrftoken + '">' +
          '<input type="hidden" name="username" value="' + username + '">' +
          '<input type="hidden" name="score" value="' + score + '" />' +
          '</form>');
        $('body').append(form);
        form.submit();
    }

    questionCounter++
    progressText.innerText = `Question ${questionCounter} of ${MAX_QUESTIONS}`
    progressBarFull.style.width = `${(questionCounter/MAX_QUESTIONS) * 100}%`
    
    const questionsIndex = Math.floor(Math.random() * availableQuestions.length)
    currentQuestion = availableQuestions[questionsIndex]
    question.innerText = currentQuestion.question

    choices.forEach(choice => {
        const number = choice.dataset['number']
        choice.innerText = currentQuestion['choice' + number]
    })

    availableQuestions.splice(questionsIndex, 1)

    acceptingAnswers = true
}

choices.forEach(choice => {
    choice.addEventListener('click', e => {
        if(!acceptingAnswers) return

        acceptingAnswers = false
        const selectedChoice = e.target
        const selectedAnswer = selectedChoice.dataset['number']

        let classToApply = selectedAnswer == currentQuestion.answer ? 'correct' : 'incorrect'

        if(classToApply === 'correct') {
            incrementScore(SCORE_POINTS)
        }

        selectedChoice.parentElement.classList.add(classToApply)

        setTimeout(() => {
            selectedChoice.parentElement.classList.remove(classToApply)
            getNewQuestion()

        }, 0)
    })
})

incrementScore = num => {
    score +=num
}

startGame()