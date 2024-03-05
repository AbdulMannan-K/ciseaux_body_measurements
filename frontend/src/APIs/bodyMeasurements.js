import axios from 'axios';

const API_URL = 'http://localhost:3005/';  


const process_video = async (data) => {
    try {
        const response = await axios.post(`${API_URL}/process_video`, data);
        return response;
    } catch (error) {
        alert("Error occured")
    }
}
const get_result_image = async (data) => {
    try {
        const response = await axios.post(`${API_URL}/get_result_image/`, data);
        return response;
    } catch (error) {
        alert("Error occured")
    }
}


const bodyMeasurements={ process_video, get_result_image}
export default bodyMeasurements;
