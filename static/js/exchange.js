$(document).ready(function () {
    const $img = $("#product-img");
    const transactionId = new URLSearchParams(window.location.search).get(
        "transaction",
    );
    const orderId = new URLSearchParams(window.location.search).get("orderId");
    const $modalOverlay = $("#modalOverlay");
    const $redeemModal = $("#redeemModal");
    const $giftModal = $("#giftModal");
    const $redeemBtn = $("#redeemBtn");
    const $giftBtn = $("#giftBtn");

    // 取得 CSRF token
    function getCsrfToken() {
        return $("#csrf_token").val();
    }

    // 顯示 Modal
    function openModal(type) {
        $modalOverlay.removeClass("hidden").addClass("flex");
        closeAllModals();
        if (type === "redeem") $redeemModal.removeClass("hidden");
        if (type === "gift") $giftModal.removeClass("hidden");
    }

    // 關閉所有 Modal
    function closeAllModals() {
        $redeemModal.addClass("hidden");
        $giftModal.addClass("hidden");
    }

    // 關閉整個 overlay
    function closeModal() {
        $modalOverlay.removeClass("flex").addClass("hidden");
        closeAllModals();
    }

    // 設定商品資料
    function renderProductInfo(info) {
        const path = staticPathByExchange + info.img_path + ".jpg";
        $img.attr("src", path).attr("alt", info.name);
        $("#product-name").text(info.name);
        $("#product-description").text(info.description);
        $("#product-time").text(`活動期間：${info.time}`);
        $("#product-stock").text(`剩餘數量：${info.quentity}`);
        $("#amount").attr("max", info.quentity);
        $("#orderBarcode").attr("src", staticPathByExchange + info.barcode_path + ".png");
        $("#transactionBarcode").attr("src", "/transactionBarcode/" + transactionId + ".png");
    }

    // 從後端取得商品資料
    function getProductInfo() {
        $.ajax({
            type: "POST",
            url: "/exchange/getProductInfo/",
            data: JSON.stringify({ transactionId, orderId }),
            headers: { "X-CSRFToken": getCsrfToken() },
            contentType: "application/json",
            dataType: "json",
            success: function (res) {
                const info = res.productInfo?.[0];
                if (info) {
                    renderProductInfo(info);
                    applyGlowIfReady();
                } else {
                    console.error("無法取得商品資料");
                }
            },
        });
    }

    // 確認 transactionId 合法
    function confirmTransaction() {
        $.ajax({
            type: "POST",
            url: "/confirmTransactionID/",
            data: JSON.stringify({ transactionID: transactionId, orderId }),
            headers: { "X-CSRFToken": getCsrfToken() },
            contentType: "application/json",
            dataType: "json",
            success: function (res) {
                if (res.success) {
                    getProductInfo();
                } else {
                    console.error("Transaction ID 驗證失敗");
                }
            },
        });
    }

    // 設定發光效果
    function applyGlowIfReady() {
        if ($img.length === 0) return;
        const colorThief = new ColorThief();

        function applyGlow() {
            const [r, g, b] = colorThief.getColor($img[0]);
            $img.css("box-shadow", `0 0 100px 10px rgba(${r}, ${g}, ${b}, 1)`);
        }

        $img[0].complete ? applyGlow() : $img.on("load", applyGlow);
    }

    $("#giftForm").submit(function (e) {
        e.preventDefault();
        const sender = $("#sender").val();
        const receiver = $("#receiver").val();
        const amount = $("#amount").val();
        let message = $("#message").val();
        message = message.replace(/[\r\n]/g, ""); // 去除換行符號
        message = message.replace(/^\s+|\s+$/g, ""); // 去除前後空白

        message = message === "你的朋友甚麼都沒有留下" ? "" : message;
        if (sender === "") {
            alert("請輸入您的暱稱!");
            return;
        }

        if (receiver === "") {
            alert("請輸入收件者的暱稱!");
            return;
        }

        if (sender === receiver) {
            alert("點擊兌換就可以領取了喔!");
            return;
        }

        if (amount === "") {
            alert("請輸入數量");
            return;
        } else if (
            amount <= 0 ||
            amount > parseInt($("#product-stock").text().split("：")[1])
        ) {
            alert("數量不正確");
            return;
        }

        // 檢查訊息長度與是否包含網址
        const urlPattern =
            /(http|https):\/\/|www\.|\.com|\.tw|\.org|\.net|\.edu|\.gov|\.info|\.jp|\.cn|\.hk|\.uk|\.us|\.de|\.fr|\.ru|\.kr|\.it|\.es|\.br|\.in|\.au|\.ca|\.mx|\.se|\.no|\.fi|\.dk|\.pl|\.cz|\.hu|\.ro|\.bg|\.gr|\.tr|\.il|\.ae|\.sa|\.eg|\.za|\.ng|\.ke|\.gh|\.tz|\.ug|\.rw|\.zm|\.mw|\.zw|\.na|\.bw|\.ls|\.sz|\.mu|\.sc|\.km|\.yt|\.re|\.pm|\.tf|\.wf|\.nc|\.pf|\.tv|\.vu|\.sb|\.fj|\.pg|\.ki|\.to|\.ws|\.nu|\.cx|\.cc|\.tk|\.gl|\.io|\.me|\.ly|\.am|\.fm|\.vc|\.gd|\.ms|\.sh|\.st|\.edu|\.gov|\.mil|\.int|\.biz|\.name|\.pro|\.aero|\.coop|\.museum/gi;
        if (
            message.length > 100 || urlPattern.test(message) ||
            sender.length > 20 || receiver.length > 20 ||
            urlPattern.test(sender) || urlPattern.test(receiver)
        ) {
            alert("訊息或暱稱字數過長或非法內容，請重新輸入");
            return;
        }

        const data = {
            transactionId,
            orderId,
            sender,
            receiver,
            amount,
            message,
        };
        $.ajax({
            type: "POST",
            url: "/exchange/share/",
            data: JSON.stringify(data),
            headers: { "X-CSRFToken": getCsrfToken() },
            contentType: "application/json",
            dataType: "json",
            success: function (res) {
                if (res.success) {
                    Swal.fire({
                        title: "分享成功！",
                        html: `
                            <div>
                                <a href="${res.url}" target="_blank">${res.url}</a>
                                <br>
                                <button id="copyLinkBtn" class="swal2-confirm swal2-styled" style="margin-top:10px;">複製連結</button>
                            </div>
                        `,
                        showConfirmButton: false,
                        allowOutsideClick: true, // 允許點擊外部關閉
                        didOpen: () => {
                            const copyBtn = document.getElementById(
                                "copyLinkBtn",
                            );
                            copyBtn.addEventListener("click", () => {
                                navigator.clipboard.writeText(res.url).then(
                                    () => {
                                        copyBtn.textContent = "已複製！";
                                        setTimeout(() => {
                                            location.reload();
                                        }, 800);
                                    },
                                );
                            });
                        },
                        willClose: () => {
                            // 使用者手動關掉視窗時 reload
                            location.reload();
                        },
                    });
                } else {
                    alert("分享失敗，請稍後再試");
                }
            },
            error: function () {
                alert("發生錯誤，請稍後再試");
            },
        });
    });

    // 綁定按鈕事件
    $redeemBtn.on("click", () => openModal("redeem"));
    $giftBtn.on("click", () => openModal("gift"));
    window.closeModal = closeModal;

    window.confirmAction = function () {
        alert("已送出");
        closeModal();
    };

    confirmTransaction(); // 頁面載入時先確認交易 ID
});
