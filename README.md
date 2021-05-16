# SimulatingVirusCloud

## Inspiration
Due the actual situation of pandemic we found interesting to be able to simulate a scenario in which a virus is spreading in a city and what is it's behavior.
## What it does
This application pretends to simulate a virus spreading among a city in which individuals have different roles and keep moving to different places. Keeping track of the statistics obtained in order to see how many people is infected, immune or dead at any time.
The simulation allows the user to enter different customization parameters in order to see different behaviors and patterns in a pandemic situation.
## How we built it
We built this application using OOP in Python and using AWS to distribute the computation of the pandemic behavior. 
All the data resides inside a DynamoDB  where a controller node retrieves all the information and generates the needed computation job. This jobs are sent to a SQS queue that behaves as a FIFO queue ensuring ordering. There are several workers nodes that take this jobs, compute them and then update the statistics. 
## Challenges we ran into
- Change the Simulation in order to be able to run in Cloud Computing environments.
- Learn about the different services available in AWS and choose the more suitable ones.
## Accomplishments that we're proud of
- Obtain a system that is able to work in local
- Design the Cloud environment to be able to process this Simulation
- Set properly some of the Cloud Services needed.
## What we learned
- Built a application written in Python from zero.
- Integrate different Cloud technologies from AWS 
## What's next for Simulating a virus behavior
- Obtain a functional Simulation in a Cloud environment.
- Offer a front end that keeps track of the statistics.
- Make a more complex simulation that obtain more accurate results.
