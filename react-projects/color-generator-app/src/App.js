import './App.css';
import React, { useState } from 'react';


function App() {
  const [color,setColor] = useState('');
  const [error,setError] = useState(false);
  const [list,setList] = useState([]);

  const handleSubmit =(e)=> {
    e.preventDefault();
    console.log('hello');
  }

  return (
    <>
    <section className="container">

    </section>
    <section className="colors">

    </section>
    </>
  );
}

export default App;
