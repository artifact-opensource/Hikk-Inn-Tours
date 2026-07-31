document.addEventListener("DOMContentLoaded", () => {
  let currentStep = 1;
  const totalSteps = 6;

  // DOM Elements
  const stepBadges = document.querySelectorAll(".step-badge");
  const formSteps = document.querySelectorAll(".form-step");
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSubmit = document.getElementById("btnSubmit");
  const bookingForm = document.getElementById("tourBookingForm");
  const submissionMessage = document.getElementById("submissionMessage");

  // Summary Elements
  const sumDestination = document.getElementById("sumDestination");
  const sumDuration = document.getElementById("sumDuration");
  const sumGuests = document.getElementById("sumGuests");
  const sumRooms = document.getElementById("sumRooms");
  const sumVehicles = document.getElementById("sumVehicles");
  const costAccommodation = document.getElementById("costAccommodation");
  const costTransport = document.getElementById("costTransport");
  const costActivities = document.getElementById("costActivities");
  const costTotal = document.getElementById("costTotal");

  // Pricing constants (in PKR)
  const roomRates = {
    "Luxury 5-Star / Resort": 25000,
    "Executive / 3-4 Star": 12000,
    "Budget / Standard Hotel": 6000,
    "Guesthouse / Homestay": 4500,
    "Camping / Tents": 3000
  };

  const activityPrices = {
    "Skardu Sightseeing": 3000,
    "Hunza Sightseeing": 2500,
    "Deosai Activities": 5000
  };

  const equipmentPrices = {
    "Tents": 2000,
    "Beds": 500,
    "Cookware": 300,
    "Generator": 1500,
    "First Aid Kit": 200
  };

  // Step Navigation
  function updateStepUI() {
    formSteps.forEach(step => {
      step.classList.toggle("active", parseInt(step.dataset.stepContent) === currentStep);
    });

    stepBadges.forEach(badge => {
      const stepNum = parseInt(badge.dataset.step);
      badge.classList.toggle("active", stepNum === currentStep);
    });

    btnPrev.style.display = currentStep > 1 ? "inline-block" : "none";
    btnNext.style.display = currentStep < totalSteps ? "inline-block" : "none";
    btnSubmit.style.display = currentStep === totalSteps ? "inline-block" : "none";

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  btnNext.addEventListener("click", () => {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        currentStep++;
        updateStepUI();
      }
    }
  });

  btnPrev.addEventListener("click", () => {
    if (currentStep > 1) {
      currentStep--;
      updateStepUI();
    }
  });

  // Counter Buttons
  document.querySelectorAll(".btn-counter").forEach(button => {
    button.addEventListener("click", (e) => {
      const targetId = e.currentTarget.dataset.target;
      const action = e.currentTarget.dataset.action;
      const input = document.getElementById(targetId);
      let val = parseInt(input.value) || 0;

      if (action === "inc") {
        val++;
      } else if (action === "dec") {
        const min = parseInt(input.getAttribute("min")) || 0;
        if (val > min) val--;
      }
      input.value = val;
      calculateEstimates();
    });
  });

  // Step Validation
  function validateStep(step) {
    const currentStepEl = document.querySelector(`.form-step[data-step-content="${step}"]`);
    const inputs = currentStepEl.querySelectorAll("input[required], select[required]");
    let valid = true;

    inputs.forEach(input => {
      if (!input.value || input.value.trim() === "") {
        input.focus();
        input.style.borderColor = "#ef4444";
        valid = false;
      } else {
        input.style.borderColor = "";
      }
    });

    if (step === 1) {
      const startDate = document.getElementById("startDateInput").value;
      const endDate = document.getElementById("endDateInput").value;
      if (startDate && endDate && endDate <= startDate) {
        alert("End date must be after start date");
        valid = false;
      }
    }

    return valid;
  }

  // Live Cost & Summary Calculation
  function calculateEstimates() {
    const dest = document.getElementById("destinationSelect").value;
    sumDestination.textContent = dest || "Not selected";

    const startDateVal = document.getElementById("startDateInput").value;
    const endDateVal = document.getElementById("endDateInput").value;

    let days = 1;
    if (startDateVal && endDateVal) {
      const start = new Date(startDateVal);
      const end = new Date(endDateVal);
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays > 0) days = diffDays;
    }
    sumDuration.textContent = `${days} Day${days > 1 ? 's' : ''}`;

    const adults = parseInt(document.getElementById("adultsInput").value) || 0;
    const children = parseInt(document.getElementById("childrenInput").value) || 0;
    const infants = parseInt(document.getElementById("infantsInput").value) || 0;
    const seniors = parseInt(document.getElementById("seniorsInput").value) || 0;
    const totalGuests = adults + children + infants + seniors;

    sumGuests.textContent = `${totalGuests} Guest${totalGuests !== 1 ? 's' : ''}`;

    // Rooms calculation
    const category = document.getElementById("hotelCategorySelect").value;
    const roomType = document.getElementById("roomTypeSelect").value;
    const roomCapacities = { "Single": 1, "Double": 2, "Triple": 3, "Suite": 4 };
    const roomCap = roomCapacities[roomType] || 2;

    const roomsNeeded = Math.max(1, Math.ceil(totalGuests / roomCap));
    document.getElementById("roomCountInput").value = roomsNeeded;
    sumRooms.textContent = `${roomsNeeded} Room${roomsNeeded > 1 ? 's' : ''}`;

    // Accommodation Cost
    const ratePerNight = roomRates[category] || 12000;
    const totalAccomCost = ratePerNight * roomsNeeded * days;
    costAccommodation.textContent = `PKR ${totalAccomCost.toLocaleString()}`;

    // Transport & Fleet
    const vehiclesNeeded = Math.max(1, Math.ceil(totalGuests / 6));
    sumVehicles.textContent = `${vehiclesNeeded} Vehicle${vehiclesNeeded > 1 ? 's' : ''}`;
    const baseTransport = 25000 * vehiclesNeeded;
    costTransport.textContent = `PKR ${baseTransport.toLocaleString()}`;

    // Activities & Equipment
    let actEquipCost = 0;
    document.querySelectorAll("input[name='activities']:checked").forEach(cb => {
      actEquipCost += activityPrices[cb.value] || 0;
    });
    document.querySelectorAll("input[name='equipment']:checked").forEach(cb => {
      actEquipCost += equipmentPrices[cb.value] || 0;
    });
    costActivities.textContent = `PKR ${actEquipCost.toLocaleString()}`;

    // Total Estimate
    const grandTotal = totalAccomCost + baseTransport + actEquipCost;
    costTotal.textContent = `PKR ${grandTotal.toLocaleString()}`;
  }

  // Event Listeners for Live Calculation
  const calcTriggerFields = [
    "destinationSelect", "startDateInput", "endDateInput", "hotelCategorySelect",
    "roomTypeSelect", "roomCountInput", "vehicleModelSelect"
  ];

  calcTriggerFields.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", calculateEstimates);
    }
  });

  document.querySelectorAll("input[name='activities'], input[name='equipment']").forEach(cb => {
    cb.addEventListener("change", calculateEstimates);
  });

  // Form Submission
  bookingForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!validateStep(totalSteps)) return;

    const formData = new FormData(bookingForm);
    const dataObj = {};
    formData.forEach((value, key) => {
      if (key === "activities" || key === "equipment") {
        if (!dataObj[key]) dataObj[key] = [];
        dataObj[key].push(value);
      } else {
        dataObj[key] = value;
      }
    });

    btnSubmit.disabled = true;
    btnSubmit.textContent = "Processing...";

    setTimeout(() => {
      btnSubmit.disabled = false;
      btnSubmit.textContent = "Submit Tour Reservation";
      submissionMessage.className = "submission-banner success";
      submissionMessage.style.display = "block";
      submissionMessage.innerHTML = `
        ✅ <strong>Tour Reservation Configured Successfully!</strong><br>
        Destination: <strong>${dataObj.destination}</strong> | Duration: <strong>${sumDuration.textContent}</strong><br>
        Your itinerary has been submitted to the automation system.
      `;
    }, 800);
  });

  // Initial Calculation
  calculateEstimates();
});
