// Add any interactive JavaScript functionality here

// Listen for quantity changes
document.querySelectorAll(".quantity-input").forEach(function(input) {
    input.addEventListener("change", function() {
        var productId = this.dataset.productId;
        var quantity = parseInt(this.value);

        // Send a request to update the cart quantity
        fetch("/cart/update", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                productId: productId,
                quantity: quantity
            })
        })
        .then(function(response) {
            if (response.ok) {
                // Quantity updated successfully
                console.log("Quantity updated");
            } else {
                // Handle error
                console.error("Failed to update quantity");
            }
        })
        .catch(function(error) {
            console.error("Error:", error);
        });
    });
});

// Listen for remove button clicks
document.querySelectorAll(".btn-remove").forEach(function(button) {
    button.addEventListener("click", function() {
        var productId = this.dataset.productId;

        // Send a request to remove the product from the cart
        fetch("/cart/remove", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                productId: productId
            })
        })
        .then(function(response) {
            if (response.ok) {
                // Product removed successfully
                console.log("Product removed");
                // Reload the page to update the cart
                location.reload();
            } else {
                // Handle error
                console.error("Failed to remove product");
            }
        })
        .catch(function(error) {
            console.error("Error:", error);
        });
    });
});
