const eventBox = document.getElementById('event-box')
const finalBox = document.getElementById('final-box')
const countdownBox = document.getElementById('countdown-box')

// console.log(eventBox.textContent)
const eventDate = Date.parse(eventBox.textContent)
console.log(eventDate)

const now = Date.parse(finalBox.textContent)
console.log(now)

// const myCountdown = setInterval(() => {
//     const diff = eventDate - now
//     console.log(diff)

//     // const d = Math.floor(eventDate / (1000 * 60 * 60 * 24) - (now / (1000 * 60 * 60 * 24)))
//     // const h = Math.floor((eventDate / (1000 * 60 * 60)) - (now / (1000 * 60 * 60)) % 24)
//     // const m = Math.floor((eventDate / (1000 * 60) - (now / (1000 * 60))) % 60)
//     // const s = Math.floor((eventDate / (1000) - (now / (1000))) % 60)
//     // console.log(d)
//     for (let i = 0; i<=3600000; i++) {
//         countdownBox.innerHTML = s + " seconds, "
//     }

//     if (diff > 0) {
//         countdownBox.innerHTML = d + " days, " + h + " hours, " + m + " minutes, " + s + " seconds,"
//     }else{
//         clearInterval(myCountdown)
//         countdownBox.innerHTML = "Payment has expired"
//     }
// },2000)

