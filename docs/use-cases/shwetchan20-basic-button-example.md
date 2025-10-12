# Basic Button Example

**Contributor:** shwetchan20  
**Implementation Type:** HTML + CSS  
**Difficulty Level:** Beginner  

## Description
A simple green button with white text that changes shade slightly on hover. No complex JavaScript, purely visual.

## Features
- Color changes on hover
- Responsive and mobile-friendly
- Keyboard accessible (Tab and Enter)

## Technologies Used
- HTML
- CSS

## How to Use
1. Copy the HTML and CSS code into your project.
2. Open the HTML file in a browser to see the button.
3. Modify colors, text, or styles as needed.

```html
<button class="green-button">Click Me</button>

<style>
.green-button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s;
}

.green-button:hover {
    background-color: #45a049;
}
</style>
