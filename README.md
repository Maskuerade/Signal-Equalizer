# Signal Equalizer

## Overview
The Signal Equalizer is a desktop application designed for manipulating and analyzing audio signals across various domains, including music, animal sounds, and ECG signals. It allows users to adjust the magnitude of specific frequency components through a user-friendly interface and visualize the effects in real-time.

## Features
- **Modes of Operation**:
  - **Uniform Range Mode**: Adjust the magnitude of frequency components divided into 10 equal ranges.
  - **Musical Instruments Mode**: Control the magnitude of different musical instruments in a mixed audio signal.
  - **Animal Sounds Mode**: Adjust the volume of specific animal sounds in a composite audio track.
  - **ECG Abnormalities Mode**: Modify the magnitude of arrhythmia components in ECG signals.

- **Interactive Sliders**: User-friendly sliders for real-time adjustment of frequency magnitudes.

- **Smoothing Windows**: Four types of smoothing windows (Rectangle, Hamming, Hanning, Gaussian) to customize the equalization process.

- **Linked Cine Signal Viewers**: Two synchronized viewers for input and output signals, with full control functionality (play, stop, pause, speed control, zoom, pan).

- **Spectrogram Visualization**: Real-time spectrograms for both input and output signals, with toggle options for visibility.

## Requirements
- Python 3.x
- Required libraries:
  - NumPy
  - SciPy
  - Matplotlib
  - PyQt5 (or your chosen UI framework)
  - PyQtGraph (for visualization)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/signal-equalizer.git
   cd signal-equalizer
   ```

2. Install the required libraries:
   ```bash
   pip install numpy scipy matplotlib PyQt5 pyqtgraph
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage
1. Select the desired mode from the dropdown menu.
2. Use the sliders to adjust the magnitude of frequency components or specific sounds.
3. Choose a smoothing window and customize its parameters as needed.
4. View real-time changes in the linked cine signal viewers and spectrograms.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- [SciPy](https://www.scipy.org/)
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [PyQt](https://riverbankcomputing.com/software/pyqt/intro)


## Contributors

<table>
  <tr>
    <td align="center">
    <a href="https://github.com/Youssef-Ashraf71" target="_black">
    <img src="https://avatars.githubusercontent.com/u/83988379?v=4" width="150px;" alt="Youssef Ashraf"/>
    <br />
    <sub><b>Youssef Ashraf</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/mouradmagdy" target="_black">
    <img src="https://avatars.githubusercontent.com/u/89527761?v=4" width="150px;" alt="Mourad Magdy"/>
    <br />
    <sub><b>Mourad Magdy</b></sub></a>
    <td align="center">
    <a href="https://github.com/ZiadMeligy" target="_black">
    <img src="https://avatars.githubusercontent.com/u/89343979?v=4" width="150px;" alt="Ziad Meligy"/>
    <br />
    <sub><b>Ziad Meligy</b></sub></a>
    </td>
    </td>
    <td align="center">
    <a href="https://github.com/Maskuerade" target="_black">
    <img src="https://avatars.githubusercontent.com/u/106713214?v=4" width="150px;" alt="Mariam Ahmed"/>
    <br />
    <sub><b>Mariam Ahmed</b></sub></a>
    </td>
      </tr>
 </table>

