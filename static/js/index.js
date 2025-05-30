$(function () {
    const test = true;
    var hamburger_menu_open = false;
    $options = $(".pay-alert .page .container .options div");
    $nextBtn = $("#info .pay-alert .page .btn-container button.next-btn");
    $prevBtn = $("#info .pay-alert .page .btn-container button.prev-btn");
    let selectObject = null;
    let paymentInterval = null;

    AOS.init({
        duration: 600,
        easing: "ease-in-out",
        once: true,
        delay: 100,
    });

    const lenis = new Lenis({
        duration: 1.3, // 设定滚动缓冲时间
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // 平滑缓动
        smooth: true,
        smoothTouch: false,
    });

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    function getCsrfToken() {
        return document.getElementById("csrf_token").value;
    }

    function init() {
        const groupName = $("#info .navbar ul li.current").text();
        const urlParams = new URLSearchParams(window.location.search);

        $.ajax({
            type: "POST",
            url: "/getProducts/",
            data: JSON.stringify({ group: groupName }),
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCsrfToken(), // CSRF sign
            },
            success: function (response) {
                const productContainer = document.querySelector(
                    "#info .product-grid",
                );
                productContainer.innerHTML = "";
                Object.keys(response["commodityInfo"]).forEach((key) => {
                    const value = response["commodityInfo"][key];
                    let html = creatCommodityCard(key, value);
                    productContainer.appendChild(html);
                });
            },
            error: function (error) {
                console.log(error);
            },
        });

        if (urlParams.get("transaction") && urlParams.get("orderId") && urlParams.get("email")) {
            console.log(urlParams.get("transaction"));
            console.log(urlParams.get("orderId"));
            console.log(urlParams.get("email"));
            const baseUrl = window.location.origin;
            $.ajax({
                type: "POST",
                url: "/confirmTransactionID/",
                data: JSON.stringify({
                    transactionID: urlParams.get("transaction"),
                    orderId: urlParams.get("orderId"),
                    email: urlParams.get("email"),
                }),
                contentType: "application/json",
                dataType: "json",
                headers: {
                    "X-CSRFToken": getCsrfToken(), // CSRF sign
                },
                success: function (response) {
                    if (response["success"]) {
                        window.location.href = baseUrl + "/exchange/?transaction=" +
                            urlParams.get("transaction") + "&orderId=" +
                            urlParams.get("orderId") + "&email=" +
                            urlParams.get("email");
                    }
                },
            });
        }
    }

    function creatCommodityCard(key, value) {
        const productCard = document.createElement("div");
        productCard.classList.add("product-card");
        productCard.setAttribute("data-aos", "fade-up");
        
        const img = document.createElement("img");
        const imgSrc = staticPath + value["img_path"] + ".jpg";
        
        img.src = imgSrc;
        img.alt = `${key}}`;

        const productName = document.createElement("p");
        productName.classList.add("product-name");
        productName.textContent = `${key}`;

        const productPrice = document.createElement("p");
        productPrice.classList.add("product-price");
        productPrice.textContent = `NT$${Math.floor(value["price"])}`;

        const eventTime = document.createElement("p");
        eventTime.classList.add("During-the-event");
        eventTime.textContent = `活動時間: ${value["time"]}`;
        productCard.appendChild(img);
        productCard.appendChild(productName);
        productCard.appendChild(productPrice);
        productCard.appendChild(eventTime);

        return productCard;
    }

    $("#info .navbars ul li").click(function (e) {
        console.log(window.location.origin);
        
        document.querySelectorAll("#info .navbar ul li").forEach((li) =>
            li.classList.add("disabled")
        );
        if ($(".hamburger-menu").css("display") === "flex") {
            $("#info .hamburger-pop ul li").removeClass("current");
            $("#info .navbar .hamburger-menu").trigger("click");
        }
        const groupName = $(this).text();
        if (groupName != $("#info .navbar ul li.current").text()) {
            $("#info .navbar ul li").removeClass("current");
            $(this).addClass("current");
            $.ajax({
                type: "POST",
                url: "/getProducts/",
                data: JSON.stringify({ group: groupName }),
                dataType: "json",
                headers: {
                    "X-CSRFToken": getCsrfToken(), // CSRF sign
                },
                success: function (response) {
                    const productContainer = document.querySelector(
                        "#info .product-grid",
                    );
                    productContainer.innerHTML = "";
                    Object.keys(response["commodityInfo"]).forEach(
                        (key, index) => {
                            const value = response["commodityInfo"][key];
                            setTimeout(() => {
                                let html = creatCommodityCard(
                                    key,
                                    value,
                                    index,
                                );
                                productContainer.appendChild(html);
                                AOS.refresh();
                                if (
                                    index ===
                                        Object.keys(response["commodityInfo"])
                                                .length - 1
                                ) {
                                    document.querySelectorAll(
                                        "#info .navbar ul li",
                                    ).forEach((li) =>
                                        li.classList.remove("disabled")
                                    );
                                }
                            }, index * 200);
                        },
                    );
                },
                error: function (err) {
                    alert(
                        "There is a server problem. Please try again later. (Error by navbar item click)\nError code: " +
                            err,
                    );
                },
            });
        }
    });

    $(window).scroll(function () {
        let st = $(this).scrollTop();
        if (st >= 10) {
            $("#info .navbar").css("position", "fixed");
            $("#info .navbar").addClass("ani");
        } else if (st < 10) {
            $("#info .navbar").css("position", "absolute");
            $("#info .navbar").removeClass("ani");
        }
    });

    $("#info .navbar .hamburger-menu").click(function (e) {
        if (hamburger_menu_open) {
            $(this).removeClass("open");
            $("#info .hamburger-pop").removeClass("open");
            $("body").css("overflow", "scroll");
            hamburger_menu_open = false;
        } else {
            $(this).addClass("open");
            $("#info .hamburger-pop").addClass("open");
            $("body").css("overflow", "hidden");
            hamburger_menu_open = true;
        }
    });

    function useLinepay(product, current_grouped, email) {
        $.ajax({
            type: "POST",
            url: "/linePayUrl/",
            data: JSON.stringify({
                product: product,
                group: current_grouped,
                email: email,
            }),
            headers: {
                "X-CSRFToken": getCsrfToken(), // CSRF sign
            },
            dataType: "json",
            success: function (response) {
                console.log("Product purchased successfully:", response);
                window.open(response.paymentUrl, "_self");
            },
            error: function (err) {
                console.log(err);
                alert(
                    "There is a server problem. Please try again later. (Error by card click)",
                );
            },
        });
    }

    function paymentAtCounter(product, current_grouped, callback) {
        $.ajax({
            type: "POST",
            url: "/payByCounter/",
            data: JSON.stringify({ group: current_grouped, product: product }),
            dataType: "json",
            headers: {
                "X-CSRFToken": getCsrfToken(), // CSRF sign
            },
            success: function (response) {
                callback(response["barcode"]);
            },
            error: function (err) {
                console.log(err);
                alert(
                    "There is a server problem. Please try again later. (Error by card click)",
                );
            },
        });
    }

    function updatePage(barcode, callback) {
        const src = staticPath + barcode + ".png";
        $("#info .pay-alert .page .container .barcode img").attr("src", src);
        $("#info .pay-alert .page .container .barcode img").attr(
            "alt",
            "barcode",
        );
        $("#info .pay-alert .page .container .options").css("display", "none");
        $("#info .pay-alert .page .container .barcode").css("display", "block");
        callback();
    }

    const steps = [".options", ".email", ".barcode"];
    let currentStep = 0;

    const updateView = () => {
        console.log(currentStep);
        
        function startPollingPayment(barcode, email = $("#email").val()) {
            paymentInterval = setInterval(() => {
                $.ajax({
                    type: "POST",
                    url: "/payByCounterConfirmPayStatus/",
                    data: JSON.stringify({
                        product: selectObject,
                        group: $("#info .navbar ul li.current").text(),
                        email: email,
                    }),
                    headers: {
                        "X-CSRFToken": getCsrfToken(), // CSRF sign
                    },
                    dataType: "json",
                    success: function (response) {
                        if (response.status === "paid") {
                            clearInterval(paymentInterval);
                            paymentInterval = null;
                            alert("付款成功！");
                        }
                    },
                    error: function () {
                        console.error("確認付款時發生錯誤");
                    },
                });
            }, 3000); // 每 3 秒POST一次
        }

        steps.forEach((selector, index) => {
            const el = document.querySelector(selector);
            if (index === currentStep) {
                el.classList.add("active");
            } else {
                el.classList.remove("active");
            }
        });

        const prevBtn = document.querySelector(".prev-btn");

        prevBtn.classList.toggle("gray", currentStep === 0);
        prevBtn.disabled = currentStep === 0;

        function checkEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        }

        if (currentStep === steps.length - 1) {
            $nextBtn.addClass("gray");
            const email = $("#email").val();
            const group = $("#info .navbars ul li.current").text();
            if (
                !email || !group || !selectObject || email == null ||
                group == null || selectObject == "null" || !checkEmail(email)
            ) {
                currentStep = steps.length - 2;
                $("#email").css("border-color", "#d13131");
                $("#email").css("box-shadow", "0 0 8px rgba(198, 66, 66, 0.4)");
                $("#email").attr("placeholder", "Email欄位錯誤或為空");
                updateView();
            } else {
                let value = $(
                    "#info .pay-alert .page .container .options div.selected",
                ).data("value");
                if (value == 1) {
                    console.log(selectObject);
                    paymentAtCounter(selectObject, group, (barcode) => {
                        const src = staticPath + barcode + ".png";
                        $("#info .pay-alert .page .container .barcode img")
                            .attr("src", src);
                        $("#info .pay-alert .page .container .barcode img")
                            .attr("alt", "barcode");
                        if (test) {
                            $.ajax({
                                type: "POST",
                                url: "/payByCounterTest/",
                                data: JSON.stringify({
                                    product: selectObject,
                                    group: $("#info .navbar ul li.current").text(),
                                    email: email,
                                    barcode: $("#info .pay-alert .page .container .barcode img").attr("src"),
                                }),
                                headers: {
                                    "X-CSRFToken": getCsrfToken(), // CSRF sign
                                },
                                dataType: "",
                                success: function (response) {
                                    if (response.url) {
                                        window.location.href = response.url;
                                    } else {
                                        console.log("No URL returned in response:", response);
                                    }
                                },
                                error: function (e) {
                                    console.log("An error occurred during testing: ", e);
                                },
                            });
                        }
                    });
                } else {
                    useLinepay(selectObject, group, email);
                }
            }
        } else {
            $nextBtn.removeClass("gray");
        }
    };

    document.querySelector(".next-btn").addEventListener("click", () => {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateView();
        }
    });

    document.querySelector(".prev-btn").addEventListener("click", () => {
        if (currentStep > 0) {
            currentStep--;
            updateView();
            if (paymentInterval) {
                clearInterval(paymentInterval);
                paymentInterval = null;
            }
        }
    });

    updateView();

    $options.on("click", function () {
        $options.removeClass("selected");
        $(this).addClass("selected");
        selectedOption = $(this).data("value");
        $nextBtn.addClass("visible");
        $prevBtn.addClass("visible");
    });

    $("#product-grid").on("click", ".product-card", function () {
        const product = $(this).find(".product-name").text().replace(
            /(\d+\s*[件瓶包盒杯])$/,
            "",
        );
        $("#info .pay-alert").css("display", "flex");
        $("#info .pay-alert .page").addClass(
            "ani_show",
        );
        $("#info .pay-alert .page").removeClass(
            "ani_disappear",
        );
        window.scrollTo({
            top: document.querySelector("#info").offsetTop,
            behavior: "smooth",
        });
        $("body").css("overflow-y", "hidden");
        lenis.stop();
        selectObject = product;
    });

    $("#info .pay-alert .page .cancel i").click(function (e) {
        $("#info .pay-alert .page").removeClass("ani_show");
        $("#info .pay-alert .page").addClass("ani_disappear");
        currentStep = 0;
        updateView();
        setTimeout(() => {
            $("#info .pay-alert").css("display", "none");
        }, 800);
        if (!$($prevBtn).hasClass("gray")) {
            $("#info .pay-alert .page .container .barcode img").attr("src", "");
            $("#info .pay-alert .page").removeClass("ani_show");
            $("#info .pay-alert .page").addClass("ani_disappear");
            setTimeout(() => {
                $("#info .pay-alert .page").addClass(
                    "ani_show",
                );
                $("#info .pay-alert .page").removeClass(
                    "ani_disappear",
                );
                $nextBtn.removeClass("gray");
                $prevBtn.addClass("gray");
                $("#info .pay-alert .page .container .options").css(
                    "display",
                    "flex",
                );
            }, 800);
        }
        if (paymentInterval) {
            clearInterval(paymentInterval);
            paymentInterval = null;
        }
        selectedOption = null;
        selectObject = null;
        $nextBtn.removeClass("visible");
        $prevBtn.removeClass("visible");
        $options.removeClass("selected");
        $("body").css("overflow-y", "scroll");
        lenis.start();
    });

    init();
});
