$(document).ready(function () {
    const $img = $("#product-img");
    const transactionId = new URLSearchParams(window.location.search).get(
        "transaction",
    );
    console.log(transactionId);
    
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
    function renderProductInfo(info, stock, code1) {
        const path = staticPathByExchange + info.img_path + ".jpg";
        $img.attr("src", path).attr("alt", info.name);
        $("#product-name").text(info.name);
        $("#product-description").text(info.description);
        $("#product-time").text(`活動期間：${info.time}`);
        $("#product-stock").text(`剩餘數量：${stock}`);
        $("#amount").attr("max", info.quentity);
        $("#orderBarcode").attr("src", staticPathByExchange + info.barcode_path + ".png");
        $("#transactionBarcode").attr("src", "/transactionBarcode/" + code1 + ".png");
    }

    // 從後端取得商品資料
    function getProductInfo(stock, code1) {
        $.ajax({
            type: "POST",
            url: "/exchange/getProductInfo/",
            data: JSON.stringify({ transactionId, orderId }),
            headers: { "X-CSRFToken": getCsrfToken() },
            contentType: "application/json",
            dataType: "json",
            success: function (res) {
                const info = res.productInfo?.[0];
                console.log("商品資訊:", info);
                if (info) {
                    renderProductInfo(info, stock, code1);
                    applyGlowIfReady();
                } else {
                    console.error("無法取得商品資料");
                }
            },
        });
    }

    function init() {
        // 確認 transactionId 合法
        console.log("Current URL:", window.location.href);
        const url = window.location.href;
        $.ajax({
            type: "POST",
            url: "/exchange/sharesInit/",
            data: JSON.stringify({ "url": url }),
            headers: { "X-CSRFToken": getCsrfToken() },
            dataType: "json",
            success: function (response) {
                if (response.status === "success") {
                    console.log("交易 ID 確認成功");
                    getProductInfo(response.stock, response.code1);
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

    // 綁定按鈕事件
    $redeemBtn.on("click", () => openModal("redeem"));
    $giftBtn.on("click", () => openModal("gift"));
    window.closeModal = closeModal;

    window.confirmAction = function () {
        alert("已送出");
        closeModal();
    };

    init();
});
