import React, { useState } from 'react';
import axios from 'axios';
import bodyMeasurements from './APIs/bodyMeasurements';
import { Button, Modal, Form, Table, Dropdown, Row, Col, Container } from 'react-bootstrap';

function App() {
  const [videoFile, setVideoFile] = useState(null);
  const [height, setHeight] = useState(null);

  const [outputImagePath, setOutputImagePath] = useState(null);
  const [measurements, setMeasurements] = useState(null)
  const handleFileChange = (event) => {
    setVideoFile(event.target.files[0]);
  };


  const handleChange = (event, key) => {
    const { value } = event.target;
    setMeasurements(prevState => ({
      ...prevState,
      [key]: value
    }));
  };
  const handleSubmit = async () => {

    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('height', height);


    try {
      const response = await bodyMeasurements.process_video(formData);

      if (!response.data || !response.data.output_image_path) {
        throw new Error('Error processing video');
      }
      setMeasurements(response.data.measurements)
      const imageResponse = await axios.get(`http://127.0.0.1:3005/get_result_image/${response.data.output_image_path}`, {
        responseType: 'blob'
      });

      if (!imageResponse.data) {
        throw new Error('Error fetching image');
      }

      const imageURL = URL.createObjectURL(imageResponse.data);
      setOutputImagePath(imageURL);
    } catch (error) {
      console.error(error.message);
    }
  };
  function generateHeights() {
    const heights = [];
    for (let feet = 5; feet <= 6; feet++) {
      for (let inches = 0; inches < 12; inches++) {
        heights.push(`${feet}'${inches}`);
      }
    }
    return heights;
  }
  const handleHeightChange = (event) => {
    setHeight(convertHeightToFeet(event.target.value))
  }
  function convertHeightToFeet(heightInput) {
    const heightParts = heightInput.split("'");
    if (heightParts.length !== 2) {
      throw new Error("Invalid height input format. Please use format like '5'4'");
    }

    const feet = parseInt(heightParts[0], 10);
    const inches = parseInt(heightParts[1], 10);

    if (isNaN(feet) || isNaN(inches)) {
      throw new Error("Invalid height input format. Please use format like '5'4'");
    }

    const totalFeet = feet + inches / 12;
    return totalFeet;
  }


  return (
    <div className='container'>
      <h1>Upload Video</h1>
      <div className="d-flex mb-3">
        <div className="col-4">
          <input
            type="file"
            className="form-control"
            accept="video/*"
            onChange={handleFileChange}
          />
        </div>
        <div className="col-2">
          <select className="form-select" onChange={handleHeightChange}>
            <option value="">Height</option>
            {generateHeights().map(height => (
              <option value={height}>{height}</option>
            ))}
          </select>
        </div>
        <div className="col-3">
          <Button onClick={handleSubmit} disabled={!videoFile || !height}>
            Submit
          </Button>
        </div>
      </div>

      {outputImagePath && (
        <div className=''>
          <h2>Result</h2>
          <div className='d-flex'>
            <img
              src={outputImagePath}
              alt="Processed"
              className="img-fluid rounded"
              style={{ maxWidth: "25%", height: "auto", borderRadius: "8px" }}
            />
            {measurements &&
              <div className="" style={{ marginTop: '-2vh' }}>
                <Container>
                  <h3>Measurements</h3>
                  <Row className="mb-3">
                    <Col>
                      <Form.Label>Left Arm</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.left_arm}
                        onChange={e => handleChange(e, "left_arm")}
                      />
                    </Col>
                    <Col>
                      <Form.Label>Right Arm</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.right_arm}
                        onChange={e => handleChange(e, "right_arm")}
                      />
                    </Col>
                  </Row>
                  <Row className="mb-3">
                    <Col>
                      <Form.Label>Left Leg</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.left_leg}
                        onChange={e => handleChange(e, "left_leg")}
                      />
                    </Col>
                    <Col>
                      <Form.Label>Right Leg</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.right_leg}
                        onChange={e => handleChange(e, "right_leg")}
                      />
                    </Col>
                  </Row>
                  <Row className="mb-3">
                    <Col>
                      <Form.Label>Shoulders</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.shoulders}
                        onChange={e => handleChange(e, "shoulders")}
                      />
                    </Col>
                    <Col>
                      <Form.Label>Chest</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.chest}
                        onChange={e => handleChange(e, "chest")}
                      />
                    </Col>
                  </Row>
                  <Row className="mb-3">
                    <Col>
                      <Form.Label>Waist</Form.Label>
                      <Form.Control
                        type="text"
                        value={measurements.waist}
                        onChange={e => handleChange(e, "waist")}
                      />
                    </Col>
                  </Row>
                </Container>
              </div>
            }

          </div>
        </div>
      )}
    </div>
  );
}

export default App;
