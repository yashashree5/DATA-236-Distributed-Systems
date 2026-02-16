const submissionCounter = (() => {
    let count = 0;
    return () => {
        count += 1;
        return count;
    };
})();

// Arrow function to validate the form
const validateForm = (content, isChecked) => {
    if (content.trim().length <= 25) { 
        alert("Blog content should be more than 25 characters");
        return false;
    }
    if (!isChecked) {
        alert("You must agree to the terms and conditions");
        return false;
    }
    
    return true; 
};

// Main function to handle form submission
const handleSubmit = (event) => {
    event.preventDefault();

    // Getting all form values
    const blogTitle = document.getElementById("blogTitle").value;
    const authorName = document.getElementById("authorName").value;
    const email = document.getElementById("email").value;
    const blogContent = document.getElementById("blogContent").value;
    const category = document.getElementById("category").value;
    const isChecked = document.getElementById("termsCheckbox").checked;

    // Validate the form
    if (!validateForm(blogContent, isChecked)) {
        return; // Stop if validation fails
    }

    // Alert shows up only when validation passes
    alert("Blog published successfully!");

    // Convert form data to JSON and log it
    const formData = {
        blogTitle: blogTitle,
        authorName: authorName,
        email: email,
        blogContent: blogContent,
        category: category,
        termsAccepted: isChecked
    };

    const jsonString = JSON.stringify(formData, null, 2);
    console.log("JSON String:");
    console.log(jsonString);

    // Parse JSON and destructure title and email
    const parsedObject = JSON.parse(jsonString);
    const { blogTitle: title, email: userEmail } = parsedObject;

    console.log("Destructured Title:", title);
    console.log("Destructured Email:", userEmail);

    // Spread operator to add submissionDate
    const updatedObject = {
        ...parsedObject,
        submissionDate: new Date().toLocaleString()
    };

    console.log("Updated Object with Spread:");
    console.log(updatedObject);

    // Log submission count using closure
    const count = submissionCounter();
    console.log("Form submitted " + count + " time(s).");
};