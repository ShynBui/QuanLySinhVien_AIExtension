'use strict';



/**
 * add event on element
 */


const addEventOnElem = function (elem, type, callback) {
  if (elem.length > 1) {
    for (let i = 0; i < elem.length; i++) {
      elem[i].addEventListener(type, callback);
    }
  } else {
    elem.addEventListener(type, callback);
  }
}



/**
 * navbar toggle
 */

const navbar = document.querySelector("[data-navbar]");
const navTogglers = document.querySelectorAll("[data-nav-toggler]");
const navLinks = document.querySelectorAll("[data-nav-link]");
const overlay = document.querySelector("[data-overlay]");

const toggleNavbar = function () {
  navbar.classList.toggle("active");
  overlay.classList.toggle("active");
}

addEventOnElem(navTogglers, "click", toggleNavbar);

const closeNavbar = function () {
  navbar.classList.remove("active");
  overlay.classList.remove("active");
}

addEventOnElem(navLinks, "click", closeNavbar);



/**
 * header active when scroll down to 100px
*/

const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

const activeElem = function () {
  if (window.scrollY > 100) {
    header.classList.add("active");
    backTopBtn.classList.add("active");
  } else {
    header.classList.remove("active");
    backTopBtn.classList.remove("active");
  }
}

addEventOnElem(window, "scroll", activeElem);


var countDownDate = new Date("2023-06-28T07:00:00Z").getTime();

		// Cập nhật thời gian sau mỗi 1 giây
		var x = setInterval(function() {

			// Lấy thời gian hiện tại
			var now = new Date().getTime();

			// Tính thời gian còn lại đến kỳ thi đại học
			var distance = countDownDate - now;

			// Tính số ngày, giờ, phút, giây còn lại
			var days = Math.floor(distance / (1000 * 60 * 60 * 24));
			var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
			var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
			var seconds = Math.floor((distance % (1000 * 60)) / 1000);

			// Hiển thị kết quả trong các thẻ div có id tương ứng
			document.getElementById("days").innerHTML = `<h1>
                                ${days}
                            </h1>
                            <p>Ngày</p>`
			document.getElementById("hours").innerHTML =`<h1>
                                ${hours}
                            </h1>
                            <p>Giờ</p>`
			document.getElementById("minutes").innerHTML = `<h1>
                                ${minutes}
                            </h1>
                            <p>Phút</p>`
			document.getElementById("seconds").innerHTML =  `<h1>
                                ${seconds}
                            </h1>
                            <p>Giây</p>`;
            	if (distance < 0) {
			clearInterval(x);
			document.getElementById("days").innerHTML = "0<br>Ngày";
			document.getElementById("hours").innerHTML = "0<br>Giờ";
			document.getElementById("minutes").innerHTML = "0<br>Phút";
			document.getElementById("seconds").innerHTML = "0<br>Giây";
			document.getElementById("countdown").innerHTML = "Đã đến giờ thi!";
		}
	}, 1000);